'use client';

import { useState } from 'react';
import SignupForm from '@/components/SignupForm';
import TermsModal from '@/components/TermsModal';
import VideoPlayer from '@/components/VideoPlayer';
import Image from 'next/image';

export default function Home() {
  const [showTerms, setShowTerms] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 relative overflow-hidden">
      {/* Background Video */}
      <div className="absolute inset-0 z-0">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover opacity-20"
        >
          <source src="/ETHCannes.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/80 via-blue-900/80 to-indigo-900/80"></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Hero Section with Logo and Video */}
        <main className="container mx-auto px-4 py-6 md:py-8">
          <div className="flex flex-col items-center text-center text-white mb-6">
            <div className="flex flex-row items-center justify-center gap-6 w-full mb-4">
              <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent whitespace-nowrap">
                Experience ChromaMind
              </h1>
              <Image src="/logo.png" alt="ChromaMind Logo" width={90} height={90} priority className="inline-block" />
            </div>
            <p className="text-lg md:text-xl text-purple-200 mb-6 max-w-2xl mx-auto">
              Immerse yourself in the future of audio-visual synchronization.
              Our AI-powered light system responds to your music in real-time.
            </p>
          </div>

          {/* Video Player and Signup Section */}
          <div className="mb-8 max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
              {/* Video Player */}
              <div className="lg:col-span-2">
                <VideoPlayer />
              </div>

              {/* Signup Form */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 h-[77.5%] flex flex-col justify-center">
                <h2 className="text-2xl font-bold text-white mb-6 text-center">
                  Join the Waiting List
                </h2>
                <SignupForm />
                <div className="mt-6 text-center">
                  <button
                    onClick={() => setShowTerms(true)}
                    className="text-purple-300 hover:text-white text-sm underline"
                  >
                    Terms & Conditions
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Feature Cards */}
          <div className="flex flex-wrap justify-center gap-6 mb-12">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
              <div className="text-3xl mb-3">🎵</div>
              <h3 className="text-lg font-bold text-white mb-2">Real-time Audio Analysis</h3>
              <p className="text-purple-200 text-sm">Advanced algorithms analyze rhythm, tempo, and frequency</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
              <div className="text-3xl mb-3">✨</div>
              <h3 className="text-lg font-bold text-white mb-2">AI-Powered Patterns</h3>
              <p className="text-purple-200 text-sm">Machine learning creates unique light sequences</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
              <div className="text-3xl mb-3">🎨</div>
              <h3 className="text-lg font-bold text-white mb-2">Customizable Colors</h3>
              <p className="text-purple-200 text-sm">Personalize your experience with color themes</p>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="container mx-auto px-4 py-8 text-center text-purple-300">
          <p>© 2025 ChromaMind - Revolutionizing Audio-Visual Experiences</p>
        </footer>
      </div>

      <TermsModal isOpen={showTerms} onClose={() => setShowTerms(false)} />
    </div>
  );
}
