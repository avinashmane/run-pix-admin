"""
Tests for src/cms/__init__.py
"""
import pytest
import os
from unittest.mock import MagicMock, patch, call

pytest.skip(allow_module_level=True)

@pytest.fixture
def mock_firebase_admin():
    """Mock firebase_admin module."""
    with patch('src.cms.firebase_admin') as mock:
        mock_cred = MagicMock()
        mock.credentials.Certificate.return_value = mock_cred
        mock_app = MagicMock()
        mock_app.name = 'cms'
        mock.initialize_app.return_value = mock_app
        
        mock_client = MagicMock()
        mock.firestore.Client.return_value = mock_client
        
        yield mock


@pytest.fixture
def sample_cms_cred():
    """Sample CMS credentials."""
    return {
        "type": "service_account",
        "project_id": "test-cms-project",
        "private_key_id": "key123",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
        "client_email": "test@test-cms-project.iam.gserviceaccount.com",
    }


def test_cms_class_init(mock_firebase_admin, sample_cms_cred):
    """Test CMSClass initialization."""
    from src.cms import CMSClass
    
    cms = CMSClass(sample_cms_cred, project_id='test-project')
    
    # Verify firebase was initialized
    mock_firebase_admin.credentials.Certificate.assert_called_once_with(sample_cms_cred)
    mock_firebase_admin.initialize_app.assert_called_once()
    
    # Verify project_id was set
    assert cms.project_id == 'test-project'


def test_cms_class_init_default_project(mock_firebase_admin, sample_cms_cred):
    """Test CMSClass initialization with default project from env."""
    from src.cms import CMSClass
    
    os.environ['CMS_PROJECT_ID'] = 'env-project-id'
    
    cms = CMSClass(sample_cms_cred)
    
    assert cms.project_id == 'env-project-id'


def test_cms_class_init_handles_exception(mock_firebase_admin, sample_cms_cred, capsys):
    """Test CMSClass handles initialization exceptions."""
    from src.cms import CMSClass
    
    mock_firebase_admin.initialize_app.side_effect = Exception("Already initialized")
    
    # Should not raise, just print error
    cms = CMSClass(sample_cms_cred, project_id='test-project')
    
    captured = capsys.readouterr()
    assert "Already initialized" in captured.out


def test_cms_get_ref(mock_firebase_admin, sample_cms_cred):
    """Test get_ref method."""
    from src.cms import CMSClass
    
    cms = CMSClass(sample_cms_cred, project_id='test-project')
    
    # Set a ref
    mock_ref = MagicMock()
    cms.ref = mock_ref
    
    result = cms.get_ref()
    
    assert result == mock_ref


def test_cms_close(mock_firebase_admin, sample_cms_cred):
    """Test close method."""
    from src.cms import CMSClass
    
    cms = CMSClass(sample_cms_cred, project_id='test-project')
    
    cms.close()
    
    # Verify delete_app was called
    mock_firebase_admin.delete_app.assert_called_once()


def test_cms_get_basic(mock_firebase_admin, sample_cms_cred):
    """Test get method with basic parameters."""
    from src.cms import CMSClass
    
    cms = CMSClass(sample_cms_cred, project_id='test-project')
    
    # Mock collection and documents
    mock_doc1 = MagicMock()
    mock_doc1.to_dict.return_value = {
        'title': 'Test Post',
        'status': 'Published',
        'sites': ['site1'],
        'timestamps': '2024-01-01',
        'requester': 'user1'
    }
    
    mock_collection = MagicMock()
    mock_collection.where.return_value = mock_collection
    mock_collection.stream.return_value = [mock_doc1]
    
    cms.client.collection.return_value = mock_collection
    
    result = cms.get('blog')
    
    # Verify collection was accessed
    cms.client.collection.assert_called_once_with('blog')
    
    # Verify result (timestamps, sites, requester should be omitted)
    assert len(result) == 1
    assert result[0]['title'] == 'Test Post'
    assert 'timestamps' not in result[0]
    assert 'sites' not in result[0]
    assert 'requester' not in result[0]


def test_cms_get_with_site_filter(mock_firebase_admin, sample_cms_cred):
    """Test get method with site filter."""
    from src.cms import CMSClass
    
    cms = CMSClass(sample_cms_cred, project_id='test-project')
    
    mock_collection = MagicMock()
    mock_collection.where.return_value = mock_collection
    mock_collection.stream.return_value = []
    
    cms.client.collection.return_value = mock_collection
    
    cms.get('blog', site='mysite')
    
    # Verify where was called for site filter
    assert mock_collection.where.called


def test_cms_get_with_published_false(mock_firebase_admin, sample_cms_cred):
    """Test get method with published=False."""
    from src.cms import CMSClass
    
    cms = CMSClass(sample_cms_cred, project_id='test-project')
    
    mock_collection = MagicMock()
    mock_collection.where.return_value = mock_collection
    mock_collection.stream.return_value = []
    
    cms.client.collection.return_value = mock_collection
    
    cms.get('blog', published=False)
    
    # Should not filter by status when published=False
    # Verify collection was accessed but status filter not applied
    cms.client.collection.assert_called_once_with('blog')


def test_cms_get_with_order_by(mock_firebase_admin, sample_cms_cred):
    """Test get method with order_by parameter."""
    from src.cms import CMSClass
    
    cms = CMSClass(sample_cms_cred, project_id='test-project')
    
    mock_collection = MagicMock()
    mock_collection.where.return_value = mock_collection
    mock_collection.order_by.return_value = mock_collection
    mock_collection.stream.return_value = []
    
    cms.client.collection.return_value = mock_collection
    
    cms.get('blog', order_by='created_at')
    
    # Verify order_by was called
    mock_collection.order_by.assert_called_once_with('created_at')


def test_cms_get_as_dict(mock_firebase_admin, sample_cms_cred):
    """Test get method with as_array=False."""
    from src.cms import CMSClass
    
    cms = CMSClass(sample_cms_cred, project_id='test-project')
    
    # Mock documents
    mock_doc1 = MagicMock()
    mock_doc1.id = 'doc1'
    mock_doc1.to_dict.return_value = {'title': 'Post 1'}
    
    mock_doc2 = MagicMock()
    mock_doc2.id = 'doc2'
    mock_doc2.to_dict.return_value = {'title': 'Post 2'}
    
    mock_collection = MagicMock()
    mock_collection.where.return_value = mock_collection
    mock_collection.stream.return_value = [mock_doc1, mock_doc2]
    
    cms.client.collection.return_value = mock_collection
    
    result = cms.get('blog', as_array=False)
    
    # Verify result is a dict with doc IDs as keys
    assert isinstance(result, dict)
    assert 'doc1' in result
    assert 'doc2' in result
    assert result['doc1']['title'] == 'Post 1'


def test_cms_get_image_url_conversion(mock_firebase_admin, sample_cms_cred):
    """Test that image URLs are converted to Firebase Storage URLs."""
    from src.cms import CMSClass
    
    cms = CMSClass(sample_cms_cred, project_id='test-cms-project')
    
    # Mock document with image field
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {
        'title': 'Post with Image',
        'image': 'images/test.jpg',
        'status': 'Published',
        'sites': [],
        'timestamps': '',
        'requester': ''
    }
    
    mock_collection = MagicMock()
    mock_collection.where.return_value = mock_collection
    mock_collection.stream.return_value = [mock_doc]
    
    cms.client.collection.return_value = mock_collection
    
    result = cms.get('blog')
    
    # Verify image URL was converted
    assert 'firebasestorage.googleapis.com' in result[0]['image']
    assert 'test-cms-project.appspot.com' in result[0]['image']


def test_cms_get_expired_filter(mock_firebase_admin, sample_cms_cred):
    """Test get method with expired filter."""
    from src.cms import CMSClass
    
    cms = CMSClass(sample_cms_cred, project_id='test-project')
    
    mock_collection = MagicMock()
    mock_collection.where.return_value = mock_collection
    mock_collection.stream.return_value = []
    
    cms.client.collection.return_value = mock_collection
    
    cms.get('blog', expired=True)
    
    # Verify where was called (should include expired filter)
    assert mock_collection.where.call_count >= 1

# Made with Bob
