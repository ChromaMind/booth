# Supabase Backend Setup

## 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the project to be ready (this may take a few minutes)

## 2. Get Project Credentials

1. In your Supabase dashboard, go to Settings > API
2. Copy the following values:
   - Project URL
   - Anon/public key

## 3. Set Environment Variables

Create a `.env.local` file in your project root:

```bash
NEXT_PUBLIC_SUPABASE_URL=your_project_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
```

## 4. Set Up Database

1. Go to SQL Editor in your Supabase dashboard
2. Copy and paste the contents of `supabase-setup.sql`
3. Run the SQL to create the waitlist table

## 5. Test the Setup

1. Start your development server: `npm run dev`
2. Fill out the signup form
3. Check your Supabase dashboard > Table Editor > waitlist to see the new entry

## Database Schema

The `waitlist` table has the following structure:

- `id`: UUID primary key
- `email`: Unique email address
- `name`: User's name
- `created_at`: Timestamp when record was created
- `updated_at`: Timestamp when record was last updated

## Security

- Row Level Security (RLS) is enabled
- Public insert policy allows anyone to register
- Email addresses are unique to prevent duplicates
- Input validation is handled both client and server-side
