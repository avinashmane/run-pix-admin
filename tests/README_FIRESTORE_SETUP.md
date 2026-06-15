# Firestore Vector Database Setup Guide

## Error: Cloud Firestore API is Disabled

If you encounter the error:
```
ERROR: Cloud Firestore API has not been used in project test-project-id before or it is disabled.
```

This means the Firestore API needs to be enabled for your Google Cloud project.

## Solution Steps

### 1. Enable Firestore API

Visit the activation URL provided in the error message:
```
https://console.developers.google.com/apis/api/firestore.googleapis.com/overview?project=YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your actual project ID from the `.env` file (`AGENT_PROJECT_ID`).

### 2. Enable the API

1. Click the **"Enable"** button on the API page
2. Wait a few minutes for the API to be fully activated
3. Retry your tests or application

### 3. Set Up Firestore Database

After enabling the API, you need to create a Firestore database:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Navigate to **Firestore Database** in the left menu
4. Click **"Create database"**
5. Choose a location (preferably close to your users)
6. Select **"Start in production mode"** or **"Start in test mode"** based on your needs
7. Click **"Enable"**

### 4. Create Vector Search Index

For vector similarity search to work, you need to create a vector index:

1. In Firestore Console, go to **Indexes** tab
2. Click **"Create Index"**
3. Configure:
   - **Collection ID**: `test_vectors` (or your collection name)
   - **Fields to index**:
     - Field: `embedding`
     - Type: **Vector**
     - Dimensions: Match your embedder dimensions (e.g., 768 for GeminiEmbedder)
     - Distance measure: **COSINE** (or your preferred metric)
   - **Query scope**: Collection
4. Click **"Create"**
5. Wait for index creation (can take several minutes)

### 5. Update Service Account Permissions

Ensure your service account has the necessary permissions:

1. Go to [IAM & Admin](https://console.cloud.google.com/iam-admin/iam)
2. Find your service account
3. Add these roles if not present:
   - **Cloud Datastore User** (for Firestore operations)
   - **Firebase Admin** (for full Firebase access)

### 6. Environment Variables

Ensure your `.env` file has the correct configuration:

```env
AGENT_PROJECT_ID=your-project-id
SERVICE_ACCOUNT={"type":"service_account","project_id":"your-project-id",...}
```

## Testing

After setup, run the tests:

```bash
# Run all Firestore tests
pytest tests/test_indiathon_firestore_vectordb.py -v

# Run specific test
pytest tests/test_indiathon_firestore_vectordb.py::TestFirestoreVectorDB::test_connection -v
```

## Common Issues

### Issue: "Permission Denied"
**Solution**: Check service account permissions in IAM

### Issue: "Index not found"
**Solution**: Create the vector index as described in step 4

### Issue: "Quota exceeded"
**Solution**: Check your Firebase/GCP quotas and upgrade if needed

### Issue: "Invalid embedding dimensions"
**Solution**: Ensure the vector index dimensions match your embedder's output dimensions

## Additional Resources

- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Vector Search in Firestore](https://firebase.google.com/docs/firestore/vector-search)
- [Service Account Setup](https://cloud.google.com/iam/docs/service-accounts)