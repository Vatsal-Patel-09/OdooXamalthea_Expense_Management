# 📦 Supabase Storage Setup Guide

## Quick Setup for Receipt Uploads

### Step 1: Create Storage Bucket

1. Open your Supabase project dashboard
2. Navigate to **Storage** in the left sidebar
3. Click **"New bucket"**
4. Fill in the details:
   - **Name:** `receipts`
   - **Public bucket:** ✅ Enabled (check this box)
   - Click **"Create bucket"**

### Step 2: Set Bucket Policies

Click on the `receipts` bucket, then go to **Policies** tab and add these policies:

#### Policy 1: Allow Authenticated Uploads
```sql
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'receipts');
```

#### Policy 2: Allow Public Reads
```sql
CREATE POLICY "Allow public reads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'receipts');
```

#### Policy 3: Allow Authenticated Deletes
```sql
CREATE POLICY "Allow authenticated deletes"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'receipts');
```

### Step 3: Test the Setup

Use the test page (already open in your browser):

1. **Login** with your credentials
2. **Upload Receipt** section:
   - Click to select a file (image or PDF)
   - Click "Upload File"
   - Should return success with URL

### Alternative: Quick SQL Setup

If you prefer SQL, run this in Supabase SQL Editor:

```sql
-- Create the bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('receipts', 'receipts', true)
ON CONFLICT (id) DO NOTHING;

-- Add policies
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'receipts');

CREATE POLICY "Allow public reads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'receipts');

CREATE POLICY "Allow authenticated deletes"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'receipts');
```

## 📁 File Organization

Files are automatically organized by the API:

```
receipts/
  └── {company_id}/
      └── {YYYY-MM}/
          └── {uuid}.{extension}
```

Example:
```
receipts/123/2024-10/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg
```

This keeps files:
- Separated by company (security)
- Organized by month (easy cleanup)
- Uniquely named (no conflicts)

## 🔒 Security Notes

1. **Public Bucket**: Files are publicly accessible via URL
   - This is intentional for viewing receipts
   - URLs contain unique UUIDs (hard to guess)
   - Company isolation via folder structure

2. **Upload Protection**: Only authenticated users can upload
   - Token required for upload
   - Company ID from JWT token

3. **Delete Protection**: Users can only delete their company's files
   - Path validation in delete endpoint
   - Checks company_id prefix

## ✅ Verification Checklist

- [ ] Bucket `receipts` created
- [ ] Bucket is set to **public**
- [ ] Three policies added (upload, read, delete)
- [ ] Test upload works via test page
- [ ] File URL is accessible in browser

## 🐛 Troubleshooting

### "Failed to upload file: 404"
- Bucket doesn't exist or wrong name
- Create bucket named exactly `receipts`

### "Failed to upload file: 403"
- Missing upload policy
- Add the "Allow authenticated uploads" policy

### Can't view uploaded file
- Bucket not set to public
- Add the "Allow public reads" policy

### Upload works but delete fails
- Missing delete policy
- Add the "Allow authenticated deletes" policy

---

**Once setup is complete, all file uploads will work seamlessly!** 🎉
