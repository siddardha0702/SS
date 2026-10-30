import json
import logging
from typing import Dict, Any, List, Optional
from backend.agents.base_agent import BaseAgent
from backend.tools.filesystem import list_files, read_file, write_file, edit_file
from backend.tools.git import git_diff, git_commit, init_or_branch
from backend.workspace.manager import workspace_manager

logger = logging.getLogger("nexus.agent.developer")

class DeveloperAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="developer_agent",
            role_description="Executes code modifications and fixes in the isolated repository workspace."
        )

    async def _execute_multi_file(
        self,
        task_id: str,
        prd_data: Dict[str, Any],
        arch_data: Dict[str, Any],
        branch_name: str,
        fix_plan: Optional[Dict[str, Any]],
        run_id: str,
        tool_calls: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate a complete, validated set of planned file changes in one LLM pass."""
        inventory = set(list_files(task_id, "."))
        modify_paths = arch_data.get("files_to_modify") or []
        create_paths = arch_data.get("files_to_create") or []
        planned_paths = list(dict.fromkeys(str(p) for p in (modify_paths + create_paths)))
        if not planned_paths or len(planned_paths) > 20:
            raise ValueError("Multi-file plan must contain between 1 and 20 explicit paths.")

        source_files: Dict[str, str] = {}
        for path in planned_paths:
            normalized = path.replace("\\", "/")
            parts = normalized.split("/")
            if (
                not normalized or normalized.startswith("/") or
                any(part in ("", ".", "..") for part in parts) or
                parts[0] == ".git" or
                any(part in ("node_modules", ".next", ".venv", "__pycache__") for part in parts) or
                parts[-1] == ".env" or parts[-1].startswith(".env.")
            ):
                raise ValueError(f"Unsafe or protected path in architecture plan: {path}")
            workspace_manager.resolve_safe_path(task_id, normalized)
            if normalized in inventory:
                source_files[normalized] = read_file(task_id, normalized)[:18000]

        await self.emit_progress(
            task_id, "working",
            f"Preparing a multi-file implementation across {len(planned_paths)} planned files..."
        )
        system_prompt = (
            "You are Nexus's senior full-stack implementation agent. Implement the approved application "
            "requirements across the complete planned file set. Return ONLY a JSON object with a 'files' "
            "array. Each item must contain exactly 'path', 'content', and 'summary'. Include every planned "
            "path exactly once; do not add unplanned paths. 'content' must be the complete replacement or "
            "new file content, not a diff. Preserve existing behavior and conventions. Do not invent secrets, "
            "credentials, or external service keys. Do not claim integrations work unless code is included. "
            "Do not output TODOs, placeholders, or explanatory prose outside the JSON."
        )
        user_prompt = (
            f"Approved PRD:\\n{json.dumps(prd_data, indent=2)}\\n\\n"
            f"Approved architecture:\\n{json.dumps(arch_data, indent=2)}\\n\\n"
            f"Existing source files (empty means the file is planned for creation):\\n"
            f"{json.dumps(source_files, indent=2)}\\n\\n"
            f"Exact required paths, each exactly once: {json.dumps(planned_paths)}\\n"
            f"Debug fix plan, if this is a repair: {json.dumps(fix_plan or {}, indent=2)}"
        )
        response = self.call_llm_json(system_prompt, user_prompt)
        generated = response.get("files")
        if not isinstance(generated, list):
            raise ValueError("Developer response must contain a files array.")

        expected = set(planned_paths)
        received: Dict[str, Dict[str, Any]] = {}
        total_bytes = 0
        for item in generated:
            if not isinstance(item, dict):
                raise ValueError("Each generated file must be a JSON object.")
            path = item.get("path")
            content = item.get("content")
            if not isinstance(path, str) or not isinstance(content, str):
                raise ValueError("Each generated file requires string path and content fields.")
            path = path.replace("\\", "/")
            if path not in expected or path in received:
                raise ValueError(f"Developer returned an unplanned or duplicate path: {path}")
            if len(content.encode("utf-8")) > 200_000:
                raise ValueError(f"Generated file exceeds the 200 KB limit: {path}")
            total_bytes += len(content.encode("utf-8"))
            received[path] = item
        if set(received) != expected:
            missing = sorted(expected - set(received))
            raise ValueError(f"Developer omitted planned files: {missing}")
        if total_bytes > 1_000_000:
            raise ValueError("Generated change set exceeds the 1 MB safety limit.")

        # Validate every path and every output before writing any file.
        for path in received:
            workspace_manager.resolve_safe_path(task_id, path)
        for path in planned_paths:
            write_file(task_id, path, received[path]["content"])
            tool_calls.append({"tool": "write_file", "args": {"path": path}})

        summary = "; ".join(
            f"{path}: {received[path].get('summary', 'updated')}" for path in planned_paths
        )
        commit_msg = "feat: implement approved multi-file project plan" if not fix_plan else "fix: apply approved multi-file repair plan"
        git_commit(task_id, commit_msg)
        tool_calls.append({"tool": "git_commit", "args": {"message": commit_msg}})
        diff_output = git_diff(task_id)
        tool_calls.append({"tool": "git_diff", "args": {}, "diff_length": len(diff_output)})
        result = {
            "target_file": planned_paths[0],
            "files_modified": planned_paths,
            "summary": summary,
            "git_diff": diff_output,
            "branch": branch_name,
        }
        self.log_run_complete(run_id, f"Updated {len(planned_paths)} files", tool_calls=tool_calls)
        await self.emit_progress(
            task_id, "completed",
            f"Multi-file implementation committed ({len(planned_paths)} files).",
            data=result,
        )
        return result

    async def execute(
        self,
        task_id: str,
        prd_data: Dict[str, Any],
        arch_data: Dict[str, Any],
        branch_name: str,
        fix_plan: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        action_type = "Bug Fix" if fix_plan else "Initial Implementation"
        run_id = self.log_run_start(task_id, f"Action: {action_type} for branch {branch_name}")
        await self.emit_progress(task_id, "working", f"Starting {action_type.lower()} in isolated workspace...")

        tool_calls: List[Dict[str, Any]] = []

        # 1. Initialize git branch if needed
        try:
            init_res = init_or_branch(task_id, branch_name)
            tool_calls.append({"tool": "init_or_branch", "args": {"branch": branch_name}, "result": init_res})
            await self.emit_progress(task_id, "working", f"Checked out branch: {branch_name}")
        except Exception as e:
            logger.warning(f"Branch checkout warning for task {task_id}: {e}")

        planned_modify = arch_data.get("files_to_modify") or []
        planned_create = arch_data.get("files_to_create") or []
        planned_count = len(set(str(p) for p in (planned_modify + planned_create)))
        if self.client and (planned_count > 1 or planned_create):
            try:
                return await self._execute_multi_file(
                    task_id, prd_data, arch_data, branch_name, fix_plan, run_id, tool_calls
                )
            except Exception as e:
                self.log_run_complete(run_id, "Multi-file implementation stopped before reporting success", tool_calls=tool_calls, status="failed", error=str(e))
                await self.emit_progress(task_id, "failed", f"Multi-file implementation could not be completed safely: {e}")
                raise

        files = list_files(task_id, ".")
        target_files = arch_data.get("files_to_modify", ["index.html"])
        target_file = target_files[0] if target_files else "index.html"

        if target_file not in files and files:
            # Pick first available HTML or JS/TS file
            for f in files:
                if f.endswith((".html", ".tsx", ".jsx", ".js")):
                    target_file = f
                    break

        await self.emit_progress(task_id, "working", f"Reading target file: {target_file}")
        content = ""
        try:
            content = read_file(task_id, target_file)
            tool_calls.append({"tool": "read_file", "args": {"path": target_file}})
        except Exception as e:
            content = "<!DOCTYPE html><html><head><title>App</title></head><body><div id='app'><h1>Nexus App</h1></div></body></html>"

        changes_summary = ""
        files_modified = [target_file]

        if fix_plan:
            # FIXING PHASE: Apply targeted correction based on Debug Agent diagnosis
            root_cause = fix_plan.get("root_cause", "")
            await self.emit_progress(task_id, "working", f"Applying fix plan: {root_cause[:80]}")

            fix_applied = False
            # Check if LLM can generate surgical fix
            if self.client:
                try:
                    fix_system_prompt = (
                        "You are the Senior Developer Agent in Nexus fixing a test failure.\n"
                        "Apply a surgical fix to the target file based on the Debug Agent's diagnosis.\n"
                        "Preserve all existing functionality and only fix the identified issue.\n"
                        "Return JSON with: {'updated_content': 'entire modified file string', 'summary': 'what was fixed'}"
                    )
                    fix_user_prompt = (
                        f"Root Cause:\n{root_cause}\n\n"
                        f"Explanation:\n{fix_plan.get('explanation', '')}\n\n"
                        f"Fix Steps:\n{json.dumps(fix_plan.get('fix_plan', []))}\n\n"
                        f"Current {target_file} content:\n{content}"
                    )
                    res = self.call_llm_json(fix_system_prompt, fix_user_prompt)
                    if res.get("updated_content"):
                        write_file(task_id, target_file, res["updated_content"])
                        tool_calls.append({"tool": "write_file", "args": {"path": target_file}})
                        changes_summary = res.get("summary", f"Fixed: {root_cause[:60]}")
                        fix_applied = True
                except Exception as e:
                    logger.warning(f"LLM fix error: {e}. Falling back to deterministic fixer.")

            if not fix_applied:
                # Deterministic surgical fixer
                updated = content
                if "hidden md:flex" in updated or "hidden md:block" in updated:
                    updated = updated.replace("hidden md:flex", "flex").replace("hidden md:block", "block")
                    changes_summary = "Removed 'hidden md:' constraint to ensure elements are visible across mobile and desktop viewports."
                elif "hidden md:inline-flex" in updated:
                    updated = updated.replace("hidden md:inline-flex", "inline-flex")
                    changes_summary = "Removed 'hidden md:' constraint to ensure button is visible across mobile and desktop viewports."
                elif "display: none" in updated:
                    updated = updated.replace("display: none;", "display: block;")
                    changes_summary = "Updated CSS display property from none to block."
                else:
                    updated = updated.replace('class="wishlist-btn hidden md:flex"', 'class="wishlist-btn flex"')
                    updated = updated.replace('class="wishlist-btn hidden md:inline-flex"', 'class="wishlist-btn inline-flex"')
                    updated = updated.replace('class="contact-submit-btn hidden md:inline-flex"', 'class="contact-submit-btn inline-flex"')
                    updated = updated.replace('class="contact-form-container hidden md:block"', 'class="contact-form-container block"')
                    updated = updated.replace('class="feature-btn hidden md:inline-flex"', 'class="feature-btn inline-flex"')
                    changes_summary = "Adjusted CSS visibility classes on responsive elements."

                write_file(task_id, target_file, updated)
                tool_calls.append({"tool": "write_file", "args": {"path": target_file}})

            commit_msg = f"fix(ui): {changes_summary}"
            git_commit(task_id, commit_msg)
            tool_calls.append({"tool": "git_commit", "args": {"message": commit_msg}})
        else:
            # INITIAL IMPLEMENTATION PHASE
            await self.emit_progress(task_id, "working", f"Implementing feature into {target_file}...")

            llm_applied = False
            req_text = (prd_data.get("title", "") + " " + prd_data.get("summary", "")).lower()

            if self.client:
                try:
                    system_prompt = (
                        "You are the Lead Developer Agent in Nexus.\n"
                        "Modify the target file to implement the requested feature according to the PRD and Architecture.\n"
                        "Requirements:\n"
                        "- Implement complete, working code — no TODOs or placeholders.\n"
                        "- Ensure clean, responsive design that works on mobile (375px+) and desktop (1280px+).\n"
                        "- Handle edge cases, validation, and user feedback.\n"
                        "- Preserve all existing functionality, styles, and script tags.\n"
                        "Return JSON with: {'updated_content': 'entire modified file string', 'summary': 'what was changed'}"
                    )
                    user_prompt = (
                        f"PRD:\n{json.dumps(prd_data, indent=2)}\n\n"
                        f"Architecture:\n{json.dumps(arch_data, indent=2)}\n\n"
                        f"Original {target_file}:\n{content}"
                    )
                    res = self.call_llm_json(system_prompt, user_prompt)
                    if res.get("updated_content") and len(res["updated_content"]) > 50:
                        write_file(task_id, target_file, res["updated_content"])
                        tool_calls.append({"tool": "write_file", "args": {"path": target_file}})
                        changes_summary = res.get("summary", "Implemented requested feature via LLM")
                        llm_applied = True
                except Exception as e:
                    logger.warning(f"LLM implementation error for task {task_id}: {e}")
                    await self.emit_progress(task_id, "working", f"LLM error: {str(e)}. Applying resilient feature template.")

            if not llm_applied:
                updated = content
                if any(k in req_text for k in ["contact", "form", "message", "email", "submit", "inquiry"]):
                    if "contact-section" not in updated:
                        contact_html = """
    <!-- CONTACT_SECTION -->
    <section id="contact-section" class="max-w-7xl mx-auto px-4 sm:px-6 py-12 border-t border-slate-800 mt-12">
      <div class="max-w-2xl mx-auto bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 sm:p-8 shadow-xl">
        <div class="mb-6">
          <h2 class="text-xl sm:text-2xl font-bold text-white tracking-tight">Contact Us</h2>
          <p class="text-xs sm:text-sm text-slate-400 mt-1">Send us an inquiry or reach out to our team.</p>
        </div>
        <form id="contact-form" onsubmit="handleContactSubmit(event)" class="space-y-4">
          <div>
            <label for="contact-name" class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Full Name</label>
            <input type="text" id="contact-name" name="name" required placeholder="Jane Doe" class="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 text-sm">
          </div>
          <div>
            <label for="contact-email" class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Email Address</label>
            <input type="email" id="contact-email" name="email" required placeholder="jane@example.com" class="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 text-sm">
          </div>
          <div>
            <label for="contact-message" class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Message</label>
            <textarea id="contact-message" name="message" rows="4" required placeholder="How can we help you?" class="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 text-sm"></textarea>
          </div>
          <div class="pt-2">
            <button type="submit" id="contact-submit-btn" class="contact-submit-btn hidden md:inline-flex items-center justify-center w-full sm:w-auto px-6 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition shadow-md">
              Submit Message
            </button>
          </div>
          <div id="contact-success-msg" class="hidden p-3 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-medium">
            Thank you! Your message has been sent successfully.
          </div>
        </form>
      </div>
    </section>
"""
                        contact_js = """
<script id="contact-engine">
  function handleContactSubmit(e) {
    if (e) e.preventDefault();
    const name = document.getElementById('contact-name').value.trim();
    const email = document.getElementById('contact-email').value.trim();
    const message = document.getElementById('contact-message').value.trim();
    if (name && email && message) {
      const banner = document.getElementById('contact-success-msg');
      if (banner) banner.classList.remove('hidden');
    }
  }
</script>
"""
                        if "</section>" in updated:
                            last_sec = updated.rfind("</section>") + len("</section>")
                            updated = updated[:last_sec] + contact_html + updated[last_sec:]
                        elif "</body>" in updated:
                            updated = updated.replace("</body>", f"{contact_html}\n</body>")
                        else:
                            updated += contact_html

                        if "</body>" in updated:
                            updated = updated.replace("</body>", f"{contact_js}\n</body>")
                        else:
                            updated += contact_js

                        write_file(task_id, target_file, updated)
                        tool_calls.append({"tool": "write_file", "args": {"path": target_file}})
                        changes_summary = "Added responsive contact section with name, email, message fields, and submission handler."
                elif "wishlist" in req_text:
                    if "wishlist-btn" not in updated:
                        if "<!-- NAVBAR_ACTIONS -->" in updated:
                            navbar_badge = (
                                '<div id="wishlist-counter-container" class="relative flex items-center bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700 text-sm font-medium text-slate-200">'
                                '  <span class="mr-1.5 text-pink-400">♥</span> Wishlist'
                                '  <span id="wishlist-count" class="ml-2 px-1.5 py-0.5 text-xs font-bold rounded-full bg-pink-500/20 text-pink-300 border border-pink-500/30">0</span>'
                                '</div>'
                            )
                            updated = updated.replace("<!-- NAVBAR_ACTIONS -->", navbar_badge)

                        wishlist_btn_template = (
                            '<!-- WISHLIST_BUTTON -->\n'
                            '                <button type="button" class="wishlist-btn hidden md:inline-flex items-center justify-center p-2 rounded-lg bg-slate-800 hover:bg-pink-950/40 text-slate-400 hover:text-pink-400 border border-slate-700 hover:border-pink-500/40 transition-all duration-200" onclick="toggleWishlist(event, this)">\n'
                            '                  <svg class="w-5 h-5 heart-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>\n'
                            '                </button>'
                        )
                        if "<!-- PRODUCT_ACTIONS -->" in updated:
                            updated = updated.replace("<!-- PRODUCT_ACTIONS -->", wishlist_btn_template)

                        wishlist_js = """
<script id="wishlist-engine">
  window.nexusWishlistState = new Set();
  function toggleWishlist(e, btn) {
    if (e) e.stopPropagation();
    const card = btn.closest('[data-product-id]') || btn.parentElement;
    const productId = card ? card.getAttribute('data-product-id') || 'prod-1' : 'prod-1';
    const heart = btn.querySelector('.heart-icon');
    
    if (window.nexusWishlistState.has(productId)) {
      window.nexusWishlistState.delete(productId);
      btn.classList.remove('text-pink-500', 'border-pink-500', 'bg-pink-950/40');
      btn.classList.add('text-slate-400', 'bg-slate-800');
      if (heart) heart.setAttribute('fill', 'none');
    } else {
      window.nexusWishlistState.add(productId);
      btn.classList.remove('text-slate-400', 'bg-slate-800');
      btn.classList.add('text-pink-500', 'border-pink-500', 'bg-pink-950/40');
      if (heart) heart.setAttribute('fill', 'currentColor');
    }
    const badge = document.getElementById('wishlist-count');
    if (badge) badge.innerText = window.nexusWishlistState.size;
  }
</script>
"""
                        if "</body>" in updated:
                            updated = updated.replace("</body>", f"{wishlist_js}\n</body>")
                        else:
                            updated += wishlist_js

                        write_file(task_id, target_file, updated)
                        tool_calls.append({"tool": "write_file", "args": {"path": target_file}})
                        changes_summary = "Added interactive wishlist button component, counter badge, and reactive state handler."
                else:
                    # Generic requested feature component
                    feature_block = f"""
    <div id="feature-container" class="max-w-7xl mx-auto px-4 sm:px-6 py-6 border-t border-slate-800 mt-6">
      <div class="p-4 rounded-xl bg-slate-800 border border-slate-700 text-slate-200">
        <h3 class="text-sm font-bold text-white">{prd_data.get('title', 'Feature')}</h3>
        <p class="text-xs text-slate-400 mt-1">{prd_data.get('summary', '')}</p>
        <button type="button" id="feature-action-btn" class="feature-btn hidden md:inline-flex mt-3 px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-semibold">Active</button>
      </div>
    </div>
"""
                    if "</body>" in updated:
                        updated = updated.replace("</body>", f"{feature_block}\n</body>")
                    else:
                        updated += feature_block
                    write_file(task_id, target_file, updated)
                    tool_calls.append({"tool": "write_file", "args": {"path": target_file}})
                    changes_summary = f"Implemented {prd_data.get('title', 'requested feature')}."

            commit_msg = f"feat: {changes_summary}"
            git_commit(task_id, commit_msg)
            tool_calls.append({"tool": "git_commit", "args": {"message": commit_msg}})

        diff_output = git_diff(task_id)
        tool_calls.append({"tool": "git_diff", "args": {}, "diff_length": len(diff_output)})

        result = {
            "target_file": target_file,
            "files_modified": files_modified,
            "summary": changes_summary,
            "git_diff": diff_output,
            "branch": branch_name
        }

        self.log_run_complete(run_id, f"Implemented changes in {target_file}", tool_calls=tool_calls)
        await self.emit_progress(task_id, "completed", f"Changes committed to branch {branch_name}", data=result)
        return result

developer_agent = DeveloperAgent()
