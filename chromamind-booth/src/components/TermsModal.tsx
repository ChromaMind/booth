'use client';

interface TermsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function TermsModal({ isOpen, onClose }: TermsModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
                    <div className="flex justify-between items-center">
                        <h2 className="text-2xl font-bold">Terms & Conditions</h2>
                        <button
                            onClick={onClose}
                            className="text-white hover:text-gray-200 text-2xl font-bold"
                        >
                            ×
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[60vh]">
                    <div className="space-y-4 text-gray-700">
                        <section>
                            <h3 className="font-bold text-lg text-gray-900 mb-2">1. Device Usage</h3>
                            <p className="text-sm leading-relaxed">
                                By using the ChromaMind device, you agree to use it responsibly and in accordance with all safety guidelines.
                                The device is designed for audio-visual synchronization and should not be used for any other purpose.
                            </p>
                        </section>

                        <section>
                            <h3 className="font-bold text-lg text-gray-900 mb-2">2. Safety Guidelines</h3>
                            <ul className="text-sm leading-relaxed space-y-2">
                                <li>&bull; Do not touch the device while it&#39;s in operation</li>
                                <li>&bull; Keep a safe distance from the light sources</li>
                                <li>&bull; If you experience any discomfort, immediately stop using the device</li>
                                <li>&bull; Children must be supervised by adults</li>
                                <li>&bull; Do not attempt to modify or disassemble the device</li>
                            </ul>
                        </section>

                        <section>
                            <h3 className="font-bold text-lg text-gray-900 mb-2">3. Medical Restrictions</h3>
                            <p className="text-sm leading-relaxed">
                                <strong>If you have epilepsy, heart conditions, or any medical issues that could be triggered by flashing lights or intense audio-visual experiences, you must not use this device.</strong>
                            </p>
                        </section>

                        <section>
                            <h3 className="font-bold text-lg text-gray-900 mb-2">4. Privacy & Data Collection</h3>
                            <p className="text-sm leading-relaxed">
                                We collect your name and email address for the purpose of managing the waiting list and notifying you when it's your turn.
                                Your data will be used solely for this purpose and will not be shared with third parties without your explicit consent.
                            </p>
                        </section>

                        <section>
                            <h3 className="font-bold text-lg text-gray-900 mb-2">5. Liability & Personal Responsibility</h3>
                            <p className="text-sm leading-relaxed">
                                <strong>All use is at your own risk. Any injury, damage, or loss is your sole responsibility. ChromaMind and its representatives are not liable for any injuries, damages, or losses that may occur during the use of the device. Users participate at their own risk and should follow all safety instructions provided.</strong>
                            </p>
                        </section>

                        <section>
                            <h3 className="font-bold text-lg text-gray-900 mb-2">6. Queue Management</h3>
                            <p className="text-sm leading-relaxed">
                                The waiting list operates on a first-come, first-served basis. We reserve the right to modify queue positions based on operational needs.
                                Users will be notified via email when it's their turn to use the device.
                            </p>
                        </section>

                        <section>
                            <h3 className="font-bold text-lg text-gray-900 mb-2">7. Event Participation</h3>
                            <p className="text-sm leading-relaxed">
                                This experience is part of a public event. By participating, you agree to follow all event rules and regulations.
                                The organizers reserve the right to modify or cancel the experience at any time.
                            </p>
                        </section>

                        <section>
                            <h3 className="font-bold text-lg text-gray-900 mb-2">8. Contact Information</h3>
                            <p className="text-sm leading-relaxed">
                                For questions about these terms or the ChromaMind experience, please contact our team at the booth or email us at
                                <span className="text-purple-600"> contact@chromamind.dev</span>
                            </p>
                        </section>
                    </div>
                </div>

                {/* Footer */}
                <div className="bg-gray-50 p-6 border-t">
                    <div className="flex justify-end">
                        <button
                            onClick={onClose}
                            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-200"
                        >
                            I Understand
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
} 