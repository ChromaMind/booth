'use client';

import { useState } from 'react';

// Mailchimp JSONP submit utility
const submitToMailchimp = async (
    email: string,
    fname: string
): Promise<{ success: boolean; message: string }> => {
    try {
        if (!email || !email.includes('@')) {
            return { success: false, message: 'Please enter a valid email address' };
        }
        const MAILCHIMP_URL =
            'https://xyz.us3.list-manage.com/subscribe/post-json?u=97f2ad1b066587133d068d6d9&id=17927a0bf7&f_id=0089b6e3f0';
        return new Promise((resolve) => {
            const callbackName = `mailchimpCallback_${Date.now()}`;
            (window as any)[callbackName] = (response: any) => {
                delete (window as any)[callbackName];
                if (response.result === 'success') {
                    resolve({ success: true, message: 'Thank you for subscribing!' });
                } else {
                    resolve({
                        success: false,
                        message: response.msg || 'An error occurred. Please try again.',
                    });
                }
            };
            const script = document.createElement('script');
            script.src = `${MAILCHIMP_URL}&EMAIL=${encodeURIComponent(
                email
            )}&FNAME=${encodeURIComponent(fname)}&c=${callbackName}`;
            script.onerror = () => {
                delete (window as any)[callbackName];
                resolve({
                    success: false,
                    message:
                        'Failed to connect to the subscription service. Please try again later.',
                });
            };
            document.body.appendChild(script);
        });
    } catch (error) {
        return {
            success: false,
            message: 'An error occurred. Please try again later.',
        };
    }
};

export default function SignupForm() {
    const [formData, setFormData] = useState({
        FNAME: '',
        email: '',
        acceptTerms: false
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [submitMessage, setSubmitMessage] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.acceptTerms) {
            alert('Please accept the terms and conditions');
            return;
        }
        setIsSubmitting(true);
        setSubmitMessage(null);
        // Send to Mailchimp
        const result = await submitToMailchimp(formData.email, formData.FNAME);
        setIsSubmitting(false);
        setIsSubmitted(result.success);
        setSubmitMessage(result.message);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    if (isSubmitted) {
        return (
            <div className="text-center">
                <div className="text-6xl mb-4">🎉</div>
                <h3 className="text-xl font-bold text-white mb-2">You're on the list!</h3>
                <p className="text-purple-200 mb-4">
                    We'll notify you when it's your turn to experience ChromaMind.
                </p>
                <div className="bg-purple-600 text-white px-4 py-2 rounded-lg inline-block">
                    <span className="font-bold">Position: #156</span>
                </div>
                {submitMessage && (
                    <div className="mt-4 text-purple-200">{submitMessage}</div>
                )}
            </div>
        );
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div>
                <label htmlFor="FNAME" className="block text-white text-sm font-medium mb-2">
                    Name
                </label>
                <input
                    type="text"
                    id="FNAME"
                    name="FNAME"
                    value={formData.FNAME}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
                    placeholder="Enter your name"
                />
            </div>

            <div>
                <label htmlFor="email" className="block text-white text-sm font-medium mb-2">
                    Email
                </label>
                <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
                    placeholder="Enter your email"
                />
            </div>

            <div className="flex items-start space-x-3">
                <input
                    type="checkbox"
                    id="acceptTerms"
                    name="acceptTerms"
                    checked={formData.acceptTerms}
                    onChange={handleInputChange}
                    className="mt-1 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                />
                <label htmlFor="acceptTerms" className="text-sm text-purple-200">
                    I accept the{' '}
                    <span className="text-purple-300 underline cursor-pointer">
                        terms and conditions
                    </span>
                </label>
            </div>

            <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-3 px-6 rounded-lg hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:ring-offset-2 focus:ring-offset-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
                {isSubmitting ? (
                    <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Joining...
                    </div>
                ) : (
                    'Join Waiting List'
                )}
            </button>
            {submitMessage && !isSubmitted && (
                <div className="text-center text-red-300 mt-2">{submitMessage}</div>
            )}
        </form>
    );
} 