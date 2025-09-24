import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const imagesDirectory = path.join(process.cwd(), 'public/images/gallery');
    console.log(imagesDirectory);
    
    // Check if the images directory exists
    if (!fs.existsSync(imagesDirectory)) {
      return NextResponse.json([]);
    }

    // Read all files from the images directory
    const files = fs.readdirSync(imagesDirectory);
    console.log(files);
    
    // Filter for common image file extensions
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'];
    const imageFiles = files.filter(file => 
      imageExtensions.some(ext => file.toLowerCase().endsWith(ext))
    );

    // Sort files for consistent ordering
    imageFiles.sort();

    return NextResponse.json(imageFiles);
  } catch (error) {
    console.error('Error reading images directory:', error);
    return NextResponse.json([]);
  }
}
