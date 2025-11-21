import React from "react";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans selection:bg-cyan-500 selection:text-slate-950">
      <div className="max-w-3xl mx-auto px-6 py-12 md:py-20">
        {/* Header */}
        <header className="mb-12">
          <h1 className="text-3xl md:text-5xl font-bold tracking-tighter text-white mb-2">
            CHROMA<span className="text-cyan-400">MIND</span>
          </h1>
          <h2 className="text-xl text-slate-400 font-medium">Privacy Policy</h2>
          <p className="text-sm text-slate-500 mt-2">
            Last Updated: November 2025
          </p>
        </header>

        {/* TL;DR Box - Highlighting the 'Anti-Corporate' Stance */}
        <div className="bg-slate-900/50 border border-cyan-500/20 rounded-2xl p-6 md:p-8 mb-12 backdrop-blur-sm shadow-[0_0_15px_rgba(6,182,212,0.1)]">
          <h3 className="text-cyan-400 font-bold uppercase tracking-wide text-sm mb-3">
            The TL;DR
          </h3>
          <p className="text-lg text-slate-100 leading-relaxed">
            <span className="font-bold">Your mind is your business.</span> We
            built ChromaMind to light up your potential, not to harvest your
            data. We don't want your personal details, we don't track your
            biology, and we don't sell you out. This app is a remote control for
            your light—nothing more.
          </p>
        </div>

        {/* Main Content */}
        <div className="space-y-12">
          {/* Section 1 */}
          <section>
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              1. Who We Are
            </h3>
            <p className="leading-relaxed">
              ChromaMind is a development team building light-therapy wearables.
              Since we are currently in our pre-incorporation phase, this policy
              covers the ChromaMind hardware and the companion mobile
              application.
            </p>
          </section>

          {/* Section 2 */}
          <section>
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              2. Data Collection (Or Lack Thereof)
            </h3>
            <p className="mb-4 leading-relaxed">
              We operate on a <strong>local-first</strong> philosophy. Here is
              exactly what we <em>don't</em> collect:
            </p>
            <ul className="list-disc pl-5 space-y-3 text-slate-300">
              <li>
                <strong className="text-slate-100">No Accounts:</strong> You can
                use the full functionality of the app without creating an
                account, providing an email, or setting a password.
              </li>
              <li>
                <strong className="text-slate-100">No Sensors:</strong> Our
                wearable is a light-emission device. It does not contain
                cameras, microphones, heart rate monitors, or GPS. It cannot
                "watch" or "listen" to you.
              </li>
              <li>
                <strong className="text-slate-100">No Cloud Sync:</strong> All
                your light patterns and settings are stored locally on your
                smartphone or the device itself. We do not have a server
                database of your habits.
              </li>
            </ul>
          </section>

          {/* Section 3 - Critical for App Store/Play Store Approval */}
          <section>
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              3. Device Permissions
            </h3>
            <p className="mb-4 leading-relaxed">
              To control the wearable, the app requires specific permissions
              from your phone. These are technical requirements for Bluetooth
              connectivity, not surveillance tools.
            </p>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="bg-slate-900 p-5 rounded-lg border border-slate-800">
                <h4 className="font-bold text-slate-100 mb-2">
                  Bluetooth (BLE)
                </h4>
                <p className="text-sm text-slate-400">
                  Required on both iOS and Android to send light pattern
                  commands from your phone to the headset.
                </p>
              </div>
              <div className="bg-slate-900 p-5 rounded-lg border border-slate-800">
                <h4 className="font-bold text-slate-100 mb-2">
                  Location (Android)
                </h4>
                <p className="text-sm text-slate-400">
                  On certain versions of Android,{" "}
                  <strong>Location permission</strong> is technically required
                  to scan for Bluetooth Low Energy devices. We do not access,
                  store, or track your GPS location. This is an Operating System
                  requirement, not a ChromaMind feature.
                </p>
              </div>
            </div>
          </section>

          {/* Section 4 */}
          <section>
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              4. Marketing & Tracking
            </h3>
            <p className="leading-relaxed mb-4">
              We respect your digital peace of mind.
            </p>
            <ul className="list-disc pl-5 space-y-2 text-slate-300">
              <li>
                We do not use tracking pixels (like Meta Pixel or Google
                Analytics).
              </li>
              <li>We do not collect advertising IDs.</li>
              <li>
                We do not integrate with third-party health APIs (like Apple
                Health or Google Fit).
              </li>
            </ul>
            <p className="mt-4 text-sm text-slate-500 italic">
              Note: The App Store (Apple) or Google Play Store may collect
              anonymous crash reports or download statistics. This is governed
              by their respective privacy policies.
            </p>
          </section>

          {/* Section 5 */}
          <section>
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              5. Age Requirement
            </h3>
            <p className="leading-relaxed">
              ChromaMind is designed for users aged{" "}
              <strong>16 and older</strong>. We do not knowingly support or
              design our device for children. Because we do not collect personal
              data, we cannot verify the age of our users, but we advise
              guardians to ensure minors do not use the device without
              supervision.
            </p>
          </section>

          {/* Section 6 */}
          <section>
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              6. Contact Us
            </h3>
            <p className="leading-relaxed mb-6">
              If you have questions about how the device works or this policy,
              you can reach the dev team directly.
            </p>
            <a
              href="mailto:hello@chromamind.com"
              className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-slate-950 bg-cyan-400 rounded-lg hover:bg-cyan-300 transition-colors duration-200"
            >
              hello@chromamind.com
            </a>
          </section>
        </div>

        {/* Footer */}
        <footer className="mt-20 pt-8 border-t border-slate-800 text-center text-slate-600 text-sm">
          <p>
            &copy; {new Date().getFullYear()} ChromaMind. Light up your
            potential.
          </p>
        </footer>
      </div>
    </div>
  );
}
