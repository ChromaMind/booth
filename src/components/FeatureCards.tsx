'use client';

interface FeatureCardsProps {
  className?: string;
}

const FeatureCards = ({ className = '' }: FeatureCardsProps) => {
  const features = [
    {
      icon: '🎵',
      title: 'Real-time Audio Analysis',
      description: 'Advanced algorithms analyze rhythm, tempo, and frequency'
    },
    {
      icon: '✨',
      title: 'AI-Powered Patterns',
      description: 'Machine learning creates unique light sequences'
    },
    {
      icon: '🎨',
      title: 'Customizable Colors',
      description: 'Personalize your experience with color themes'
    }
  ];

  return (
    <div className={`w-full ${className}`}>
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300"
            >
              <div className="text-3xl mb-3">{feature.icon}</div>
              <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-purple-200 text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FeatureCards;
