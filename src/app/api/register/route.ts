import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function POST(request: NextRequest) {
    try {
        const { email, FNAME } = await request.json();

        // Validate input
        if (!email || !email.includes('@') || !FNAME || FNAME.trim().length === 0) {
            return NextResponse.json(
                { error: 'Invalid email or name' },
                { status: 400 }
            );
        }

        // Check if user already exists
        const { data: existingUser } = await supabase
            .from('waitlist')
            .select('id')
            .eq('email', email)
            .single();

        if (existingUser) {
            return NextResponse.json(
                { error: 'Email already registered' },
                { status: 409 }
            );
        }

        // Insert new user
        const { data, error } = await supabase
            .from('waitlist')
            .insert([
                {
                    email: email.toLowerCase().trim(),
                    name: FNAME.trim(),
                    created_at: new Date().toISOString()
                }
            ])
            .select()
            .single();

        if (error) {
            console.error('Supabase error:', error);
            return NextResponse.json(
                { error: 'Failed to register user' },
                { status: 500 }
            );
        }

        return NextResponse.json({
            success: true,
            message: 'Successfully registered for the waiting list!',
            data
        });

    } catch (error) {
        console.error('Registration error:', error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}
