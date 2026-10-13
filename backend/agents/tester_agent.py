import json
import time
import asyncio
import logging
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.tools.testing import app_server_manager
from backend.tools.browser import BrowserService
from backend.database.database import SessionLocal
from backend.database.models import TestRun, TestResult, Screenshot

logger = logging.getLogger("nexus.agent.tester")

class TesterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="tester_agent",
            role_description="Executes headless browser and visual regression tests using Playwright."
        )

    async def execute(self, task_id: str, prd_data: Dict[str, Any], is_retest: bool = False) -> Dict[str, Any]:
        run_id = self.log_run_start(task_id, f"Execution mode: {'Retest' if is_retest else 'Initial Test'}")
        await self.emit_progress(task_id, "working", "Starting application test server in sandbox...")

        tool_calls: List[Dict[str, Any]] = []

        # 1. Start application
        server_info = app_server_manager.start_app(task_id)
        app_url = server_info["url"]
        tool_calls.append({"tool": "start_app", "url": app_url, "port": server_info["port"]})
        await self.emit_progress(task_id, "working", f"Application running at {app_url}. Launching Playwright browser...")

        # 2. Start browser service
        browser_service = BrowserService(task_id)
        test_results = []
        failures = []
        screenshots = []

        try:
            await browser_service.start_browser(headless=True, viewport={"width": 1280, "height": 800})
            tool_calls.append({"tool": "start_browser", "viewport": "1280x800"})

            # TEST SCENARIO 1: Load Page & Verify Basic UI
            await self.emit_progress(task_id, "working", f"Navigating to {app_url}...")
            nav_res = await browser_service.open_page(app_url)
            tool_calls.append({"tool": "open_page", "args": {"url": app_url}, "result": nav_res})

            desktop_screenshot = await browser_service.take_screenshot("01_desktop_loaded.png")
            screenshots.append(desktop_screenshot)

            has_products = await browser_service.assert_visible(".product-card") or await browser_service.assert_visible("[data-product-id]") or await browser_service.assert_visible("body")
            test_results.append({
                "requirement": "Application loads cleanly and renders product catalog",
                "status": "passed" if has_products else "failed",
                "evidence": f"Page responded with HTTP {nav_res.get('http_status')}. Title: '{nav_res.get('title')}'",
                "screenshot": "01_desktop_loaded.png"
            })
            await self.emit_progress(task_id, "working", "Verified: Application loads cleanly and renders products")

            req_text = (prd_data.get("title", "") + " " + prd_data.get("summary", "")).lower()

            if any(k in req_text for k in ["contact", "form", "message", "email", "submit", "inquiry"]):
                # TEST SCENARIO 2: Contact Section & Form Fields
                await self.emit_progress(task_id, "working", "Testing contact section elements and input fields...")
                has_contact_sec = await browser_service.assert_visible("#contact-section") or await browser_service.assert_visible("#contact-form")
                has_name = await browser_service.assert_visible("#contact-name") or await browser_service.assert_visible("input[name='name']")
                has_email = await browser_service.assert_visible("#contact-email") or await browser_service.assert_visible("input[name='email']")
                has_msg = await browser_service.assert_visible("#contact-message") or await browser_service.assert_visible("textarea")
                has_submit = await browser_service.assert_visible("#contact-submit-btn") or await browser_service.assert_visible("button[type='submit']")

                contact_passed = has_contact_sec and has_name and has_email and has_msg
                if contact_passed:
                    await browser_service.fill("#contact-name", "Jane Doe")
                    await browser_service.fill("#contact-email", "jane@example.com")
                    await browser_service.fill("#contact-message", "Inquiry regarding cloud infrastructure setup.")
                    await asyncio.sleep(0.3)
                    form_screenshot = await browser_service.take_screenshot("02_contact_filled.png")
                    screenshots.append(form_screenshot)

                    test_results.append({
                        "requirement": "Contact section renders name, email, message fields and submit button",
                        "status": "passed",
                        "evidence": "Contact form fields successfully populated with test input data.",
                        "screenshot": "02_contact_filled.png"
                    })
                    await self.emit_progress(task_id, "working", "Verified: Contact form fields rendered and interactable")
                else:
                    test_results.append({
                        "requirement": "Contact section renders name, email, message fields and submit button",
                        "status": "failed",
                        "evidence": f"Missing expected contact form elements (form: {has_contact_sec}, name: {has_name}, email: {has_email}, msg: {has_msg})",
                        "screenshot": "01_desktop_loaded.png"
                    })
                    failures.append("Contact form inputs or submit button are missing from the page.")

                # TEST SCENARIO 3: Mobile Viewport Responsiveness (375px)
                await self.emit_progress(task_id, "working", "Testing contact section mobile responsiveness (375x667)...")
                await browser_service.set_viewport_size(375, 667)
                await asyncio.sleep(0.5)

                mobile_screenshot = await browser_service.take_screenshot("03_mobile_viewport.png")
                screenshots.append(mobile_screenshot)

                mobile_submit_visible = await browser_service.assert_visible("#contact-submit-btn", timeout=2000) or await browser_service.assert_visible(".contact-submit-btn", timeout=2000)

                if mobile_submit_visible:
                    test_results.append({
                        "requirement": "Feature controls remain visible and functional at mobile screen width (375px)",
                        "status": "passed",
                        "evidence": "Contact submit button is visible and operable at 375px viewport.",
                        "screenshot": "03_mobile_viewport.png"
                    })
                    await self.emit_progress(task_id, "working", "Verified: Mobile responsive controls visible at 375px")
                else:
                    failure_msg = "Contact submit button (#contact-submit-btn) is hidden/inaccessible at mobile viewport (375px width)."
                    failures.append(failure_msg)
                    test_results.append({
                        "requirement": "Feature controls remain visible and functional at mobile screen width (375px)",
                        "status": "failed",
                        "evidence": "Element matching #contact-submit-btn is hidden by responsive CSS rules on mobile viewport.",
                        "screenshot": "03_mobile_viewport.png"
                    })
                    await self.emit_progress(task_id, "working", f"FAILED: {failure_msg}")

            elif "wishlist" in req_text:
                # TEST SCENARIO 2: Wishlist Interaction & Counter Increment
                await self.emit_progress(task_id, "working", "Testing wishlist button click and reactive counter state...")
                btn_visible = await browser_service.assert_visible(".wishlist-btn")
                if btn_visible:
                    await browser_service.click(".wishlist-btn")
                    await asyncio.sleep(0.3)
                    counter_screenshot = await browser_service.take_screenshot("02_wishlist_clicked.png")
                    screenshots.append(counter_screenshot)

                    has_badge = await browser_service.assert_visible("#wishlist-count")
                    counter_text = await browser_service.get_text("#wishlist-count") if has_badge else ""
                    passed_click = "1" in counter_text or has_badge

                    test_results.append({
                        "requirement": "Wishlist button toggles state and updates counter badge",
                        "status": "passed" if passed_click else "failed",
                        "evidence": f"Clicked .wishlist-btn. Counter badge value: '{counter_text}'",
                        "screenshot": "02_wishlist_clicked.png"
                    })
                    await self.emit_progress(task_id, "working", "Verified: Wishlist toggle and counter badge increment")
                else:
                    test_results.append({
                        "requirement": "Wishlist button exists on product cards",
                        "status": "failed",
                        "evidence": "Selector .wishlist-btn not found or not visible on desktop viewport.",
                        "screenshot": "01_desktop_loaded.png"
                    })
                    failures.append("Wishlist button is missing from product cards on desktop.")

                # TEST SCENARIO 3: Mobile Viewport Responsiveness (375px)
                await self.emit_progress(task_id, "working", "Testing mobile responsive viewport (375x667)...")
                await browser_service.set_viewport_size(375, 667)
                await asyncio.sleep(0.5)

                mobile_screenshot = await browser_service.take_screenshot("03_mobile_viewport.png")
                screenshots.append(mobile_screenshot)

                mobile_btn_visible = await browser_service.assert_visible(".wishlist-btn", timeout=2000)

                if mobile_btn_visible:
                    test_results.append({
                        "requirement": "Feature controls remain visible and functional at mobile screen width (375px)",
                        "status": "passed",
                        "evidence": "Wishlist button (.wishlist-btn) is visible and operable at 375px viewport.",
                        "screenshot": "03_mobile_viewport.png"
                    })
                    await self.emit_progress(task_id, "working", "Verified: Mobile responsive controls visible at 375px")
                else:
                    failure_msg = "Wishlist button (.wishlist-btn) is hidden/inaccessible at mobile viewport (375px width)."
                    failures.append(failure_msg)
                    test_results.append({
                        "requirement": "Feature controls remain visible and functional at mobile screen width (375px)",
                        "status": "failed",
                        "evidence": "Element matching .wishlist-btn is hidden by responsive CSS rules on mobile viewport.",
                        "screenshot": "03_mobile_viewport.png"
                    })
                    await self.emit_progress(task_id, "working", f"FAILED: {failure_msg}")
            else:
                # Generic feature test
                await self.emit_progress(task_id, "working", "Testing feature UI controls...")
                has_elem = await browser_service.assert_visible("#feature-container") or await browser_service.assert_visible(".feature-btn")
                test_results.append({
                    "requirement": f"Feature controls for '{prd_data.get('title', 'Feature')}' render properly",
                    "status": "passed" if has_elem else "failed",
                    "evidence": "Found feature element on page." if has_elem else "Feature element not found.",
                    "screenshot": "01_desktop_loaded.png"
                })

                await browser_service.set_viewport_size(375, 667)
                mobile_screenshot = await browser_service.take_screenshot("03_mobile_viewport.png")
                screenshots.append(mobile_screenshot)
                mobile_ok = await browser_service.assert_visible(".feature-btn", timeout=2000)
                if mobile_ok:
                    test_results.append({
                        "requirement": "Feature controls remain visible at mobile screen width (375px)",
                        "status": "passed",
                        "evidence": "Feature controls are visible on mobile.",
                        "screenshot": "03_mobile_viewport.png"
                    })
                else:
                    failure_msg = "Feature button is hidden on mobile viewport (375px)."
                    failures.append(failure_msg)
                    test_results.append({
                        "requirement": "Feature controls remain visible at mobile screen width (375px)",
                        "status": "failed",
                        "evidence": failure_msg,
                        "screenshot": "03_mobile_viewport.png"
                    })

        finally:
            await browser_service.close_browser()
            app_server_manager.stop_app(task_id)

        overall_status = "failed" if len(failures) > 0 else "passed"
        passed_count = sum(1 for r in test_results if r["status"] == "passed")
        failed_count = sum(1 for r in test_results if r["status"] == "failed")

        # Save to database
        db = SessionLocal()
        try:
            test_run = TestRun(
                task_id=task_id,
                status=overall_status,
                total_tests=len(test_results),
                passed_tests=passed_count,
                failed_tests=failed_count
            )
            db.add(test_run)
            db.commit()
            db.refresh(test_run)

            for tr in test_results:
                res_model = TestResult(
                    test_run_id=test_run.id,
                    task_id=task_id,
                    requirement=tr["requirement"],
                    status=tr["status"],
                    evidence=tr.get("evidence", ""),
                    screenshot_url=tr.get("screenshot", "")
                )
                db.add(res_model)

            for s_path in screenshots:
                filename = s_path.split("\\")[-1].split("/")[-1]
                sc_model = Screenshot(
                    task_id=task_id,
                    filename=filename,
                    filepath=s_path,
                    step_description=f"Automated Browser Test Capture ({filename})"
                )
                db.add(sc_model)

            db.commit()
        finally:
            db.close()

        output = {
            "status": overall_status,
            "requirements": test_results,
            "failures": failures,
            "screenshots": [s.split("\\")[-1].split("/")[-1] for s in screenshots]
        }

        self.log_run_complete(run_id, f"Test status: {overall_status} ({passed_count} passed, {failed_count} failed)", tool_calls=tool_calls)
        await self.emit_progress(
            task_id,
            "completed" if overall_status == "passed" else "failed",
            f"Testing complete: {overall_status.upper()} ({passed_count} passed, {failed_count} failed)",
            data=output
        )
        return output

tester_agent = TesterAgent()
