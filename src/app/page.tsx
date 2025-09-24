'use client';

import { useState } from 'react';
import SignupForm from '@/components/SignupForm';
import TermsModal from '@/components/TermsModal';
import VideoPlayer from '@/components/VideoPlayer';
import Gallery from '@/components/Gallery';
import FeatureCards from '@/components/FeatureCards';
import HowItWorks from '@/components/HowItWorks';
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
            {/* Logo on top for mobile */}
            <div className="block sm:hidden mb-2">
              <Image src="/logo.png" alt="ChromaMind Logo" width={90} height={90} priority className="inline-block" />
            </div>
            <div className="flex flex-row items-center justify-center gap-6 w-full mb-4">
              {/* Logo hidden on mobile, shown on larger screens */}
              <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Experience ChromaMind
              </h1>
              <span className="hidden sm:inline-block">
                <Image src="/logo.png" alt="ChromaMind Logo" width={90} height={90} priority className="inline-block" />
              </span>
            </div>
            <p className="text-lg md:text-xl text-purple-200 mb-6 max-w-2xl mx-auto">
              Immerse yourself in the future of audio-visual synchronization.
              Our AI-powered light system responds to your music in real-time.
            </p>
          </div>

          {/* Video Player and Signup Section */}
          <div className="mb-8 max-w-6xl mx-auto">
            <div className="grid grid-cols-1 gap-8 items-start lg:grid-cols-3">
              {/* Video Player */}
              <div className="lg:col-span-2">
                <VideoPlayer />
              </div>

              {/* Signup Form */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 h-auto flex flex-col justify-center w-full">
                <h2 className="text-2xl font-bold text-white mb-6 text-center">
                  Join the Waiting List
                </h2>
                <SignupForm />
                
                {/* Feedback Incentive */}
                <div className="mt-6 p-4 bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm rounded-xl border border-purple-400/30">
                  <div className="text-center">
                    <div className="text-2xl mb-2">🎁</div>
                    <h4 className="text-white font-semibold mb-2">Want a Free ChromaMind Device?</h4>
                    <p className="text-purple-200 text-sm mb-3">
                      Share your feedback about our VR meditation experience and enter our EthSofia raffle!
                    </p>
                    <button
                      onClick={() => window.open('https://docs.google.com/forms/d/e/1FAIpQLSeJ8XOWynkUco87CeANKhJBDDR0UipNeu-7ULqiAUuBhU270A/viewform?usp=dialog', '_blank', 'noopener,noreferrer')}
                      className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-2 px-4 rounded-lg text-sm transition-all duration-300 transform hover:scale-105"
                    >
                      📝 Give Feedback & Enter Raffle
                    </button>
                  </div>
                </div>

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

          {/* Gallery Section */}
          <div className="max-w-7xl mx-auto mt-8 mb-16">
            <Gallery />
          </div>

          {/* How ChromaMind Works Section */}
          <div className="mt-8 mb-12">
            <HowItWorks />
          </div>

          {/* Feature Cards */}
          <div className="mt-8">
            <FeatureCards />
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
