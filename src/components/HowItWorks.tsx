'use client';

interface HowItWorksProps {
  className?: string;
}

const HowItWorks = ({ className = '' }: HowItWorksProps) => {
  return (
    <div className={`w-full ${className}`}>
      <div className="text-center text-white max-w-3xl mx-auto">
        <h3 className="text-3xl font-bold mb-4">How ChromaMind Works</h3>
        <p className="text-purple-200 max-w-3xl mx-auto text-lg">
          Watch how our AI-powered system analyzes audio in real-time and creates
          synchronized light patterns that respond to the rhythm, tempo, and frequency of your music.
        </p>
      </div>
    </div>
  );
};

export default HowItWorks;
