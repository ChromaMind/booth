'use client';

import ReactPlayer from 'react-player';

export default function VideoPlayer() {
    // Remove all video-related state and refs
    return (
        <div className="w-full max-w-6xl mx-auto">
            <div className="bg-black rounded-2xl overflow-hidden shadow-2xl">
                {/* Video Container */}
                <div className="relative aspect-[16/10]">
                    <ReactPlayer
                        src="https://www.youtube.com/watch?v=YhQ9yDCir28"
                        width="100%"
                        height="100%"
                        controls
                        className="object-cover"
                    />
                </div>
                {/* Video Controls and Description remain unchanged, or remove if not needed */}
            </div>
            {/* Video Description */}
        </div>
    );
} 