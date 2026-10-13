import type { Metadata } from 'next';
import './globals.css';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { Footer } from '../components/Footer';

export const metadata: Metadata = {
  title: 'Nexus — Autonomous AI Software Engineering Team',
  description: 'Full-cycle multi-agent autonomous engineering platform from PRD to verified Pull Request.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen flex bg-[#090d16] text-slate-100 antialiased selection:bg-blue-600 selection:text-white font-sans">
        {/* Desktop Sidebar (responsive: visible on md+, hidden on mobile) */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 min-h-screen">
          {/* Global SaaS Navigation Bar */}
          <Navbar />

          {/* Main Body View */}
          <main className="flex-1 w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>

          {/* Global SaaS Footer */}
          <Footer />
        </div>
      </body>
    </html>
  );
}
