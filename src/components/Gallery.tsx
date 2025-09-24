'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';

interface GalleryProps {
  className?: string;
}

const Gallery = ({ className = '' }: GalleryProps) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [images, setImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  // Dynamically load all images from the /public/images folder
  useEffect(() => {
    const loadImages = async () => {
      try {
        // Fetch the list of images from the API route
        const response = await fetch('/api/images');
        const imageList = await response.json();
        setImages(imageList.map((img: string) => `/images/gallery/${img}`));
      } catch (error) {
        console.error('Error loading images:', error);
        // Fallback to empty array if API fails
        setImages([]);
      } finally {
        setLoading(false);
      }
    };

    loadImages();
  }, []);

  const openLightbox = (imageSrc: string, index: number) => {
    setSelectedImage(imageSrc);
    setCurrentIndex(index);
  };

  const closeLightbox = () => {
    setSelectedImage(null);
  };

  const goToNext = () => {
    const nextIndex = (currentIndex + 1) % images.length;
    setCurrentIndex(nextIndex);
    setSelectedImage(images[nextIndex]);
  };

  const goToPrevious = () => {
    const prevIndex = (currentIndex - 1 + images.length) % images.length;
    setCurrentIndex(prevIndex);
    setSelectedImage(images[prevIndex]);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowRight') goToNext();
    if (e.key === 'ArrowLeft') goToPrevious();
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Gallery Title */}
      <div className="text-center mb-8">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          ChromaMind Gallery
        </h2>
        <p className="text-purple-200 text-lg max-w-2xl mx-auto">
          Explore moments from our journey at recent events 2025, showcasing ChromaMind in action.
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          <span className="ml-3 text-white">Loading gallery...</span>
        </div>
      )}

      {/* Empty State */}
      {!loading && images.length === 0 && (
        <div className="text-center py-12">
          <p className="text-purple-200 text-lg">No images found in the gallery.</p>
        </div>
      )}

      {/* Gallery Grid */}
      {!loading && images.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
          {images.map((imageSrc, index) => (
          <div
            key={imageSrc}
            className="relative aspect-square overflow-hidden rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 hover:border-white/40 transition-all duration-300 cursor-pointer group"
            onClick={() => openLightbox(imageSrc, index)}
          >
            <Image
              src={imageSrc}
              alt={`ChromaMind Gallery Image ${index + 1}`}
              fill
              className="object-cover transition-transform duration-300 group-hover:scale-105"
              sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="absolute bottom-2 left-2 text-white text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              Image {index + 1}
            </div>
          </div>
          ))}
        </div>
      )}

      {/* Lightbox Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm"
          onClick={closeLightbox}
          onKeyDown={handleKeyDown}
          tabIndex={0}
        >
          <div className="relative max-w-7xl max-h-[90vh] w-full h-full flex items-center justify-center p-4">
            {/* Close Button */}
            <button
              onClick={closeLightbox}
              className="absolute top-4 right-4 z-10 text-white hover:text-gray-300 transition-colors"
            >
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Previous Button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                goToPrevious();
              }}
              className="absolute left-4 top-1/2 -translate-y-1/2 z-10 text-white hover:text-gray-300 transition-colors bg-black/20 rounded-full p-2"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            {/* Next Button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                goToNext();
              }}
              className="absolute right-4 top-1/2 -translate-y-1/2 z-10 text-white hover:text-gray-300 transition-colors bg-black/20 rounded-full p-2"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>

            {/* Image */}
            <div className="relative max-w-full max-h-full" onClick={(e) => e.stopPropagation()}>
              <Image
                src={selectedImage}
                alt={`ChromaMind Gallery Image ${currentIndex + 1}`}
                width={1200}
                height={800}
                className="max-w-full max-h-[80vh] object-contain rounded-lg"
                priority
              />
            </div>

            {/* Image Counter */}
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white bg-black/50 px-4 py-2 rounded-full">
              {currentIndex + 1} of {images.length}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Gallery;
