import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loading } from "@/components/ui/loading";
import { Toast } from "@/components/ui/toast";
import { ScrollGold } from "@/components/ui/scroll-gold";
import { ScrollMemory } from "@/components/ui/scroll-memory";
import { ScrollGraph } from "@/components/ui/scroll-graph";
import { useAuth } from '@/auth/AuthContext';
import ScrollProphet from '@/components/ScrollProphet';
import { Download, Github, RefreshCw, Cloud } from 'lucide-react';
import { Typography, Space, Alert, Spin } from 'antd';
import { SyncOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { toast } from 'react-toastify';

interface Integration {
  id: string;
  name: string;
  type: string;
  status: 'connected' | 'disconnected';
  credentials?: Record<string, string>;
}

interface Dataset {
  id: string;
  name: string;
  source: string;
  type: string;
  lastUpdated: string;
}

interface Session {
  id: string;
  domain: string;
  timestamp: string;
  chartPath: string;
  metadata: Record<string, any>;
  interpretation: {
    caption: string;
    metrics: Record<string, any>;
  };
  github_commit_url?: string;
}

interface ToastMessage {
  type: 'success' | 'error' | 'info';
  message: string;
}

interface GitHubExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (repoName: string, commitMessage: string) => void;
  loading: boolean;
}

interface SyncStatus {
  last_sync: string | null;
  status: 'idle' | 'syncing' | 'success' | 'error';
}

interface SyncStatusResponse {
  dropbox: SyncStatus;
  gdrive: SyncStatus;
  onedrive: SyncStatus;
}

const { Title, Text } = Typography;

const GitHubExportModal: React.FC<GitHubExportModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  loading
}) => {
  const [repoName, setRepoName] = useState('');
  const [commitMessage, setCommitMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(repoName, commitMessage);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Push to GitHub</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="repoName">Repository Name</Label>
              <Input
                id="repoName"
                value={repoName}
                onChange={(e) => setRepoName(e.target.value)}
                placeholder="my-flame-repo"
                required
              />
            </div>
            <div>
              <Label htmlFor="commitMessage">Commit Message (Optional)</Label>
              <Input
                id="commitMessage"
                value={commitMessage}
                onChange={(e) => setCommitMessage(e.target.value)}
                placeholder="Flame Upload"
              />
            </div>
            <div className="flex justify-end space-x-2">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Pushing...' : 'Push to GitHub'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

const IntegrationDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedIntegration, setSelectedIntegration] = useState<string | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<ToastMessage | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [prophetContext, setProphetContext] = useState<Record<string, any> | null>(null);
  const [prophetData, setProphetData] = useState<Record<string, any> | null>(null);
  const { token } = useAuth();
  const [selectedSessionForGitHub, setSelectedSessionForGitHub] = useState<string | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatusResponse | null>(null);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchIntegrations();
    fetchDatasets();
    fetchSessions();
    fetchSyncStatus();
  }, []);

  useEffect(() => {
    if (integrations.length > 0 || datasets.length > 0 || sessions.length > 0) {
      setProphetContext({
        domain: 'Integration Dashboard',
        data_type: 'mixed',
        metrics: ['integrations', 'datasets', 'sessions'],
        recent_activity: sessions.slice(0, 5).map(s => ({
          type: s.type,
          timestamp: s.timestamp
        }))
      });
    }
  }, [integrations, datasets, sessions]);

  const showToast = (type: ToastMessage['type'], message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 5000);
  };

  const fetchIntegrations = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/integrations');
      const data = await response.json();
      setIntegrations(data.integrations);
    } catch (err) {
      showToast('error', 'Failed to fetch integrations');
    } finally {
      setLoading(false);
    }
  };

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/datasets');
      const data = await response.json();
      setDatasets(data.datasets);
    } catch (err) {
      showToast('error', 'Failed to fetch datasets');
    } finally {
      setLoading(false);
    }
  };

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/sessions');
      const data = await response.json();
      setSessions(data.sessions);
    } catch (err) {
      showToast('error', 'Failed to fetch sessions');
    } finally {
      setLoading(false);
    }
  };

  const fetchSyncStatus = async () => {
    try {
      const response = await fetch('/api/sync/status', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setSyncStatus(data);
    } catch (error) {
      toast.error('Failed to fetch sync status');
      console.error('Error fetching sync status:', error);
    }
  };

  const connectIntegration = async (integrationId: string, credentials: Record<string, string>) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/integrations/${integrationId}/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credentials }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        showToast('success', 'Integration connected successfully');
        fetchIntegrations();
      } else {
        showToast('error', data.message);
      }
    } catch (err) {
      showToast('error', 'Failed to connect integration');
    } finally {
      setLoading(false);
    }
  };

  const disconnectIntegration = async (integrationId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/integrations/${integrationId}/disconnect`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.status === 'success') {
        showToast('success', 'Integration disconnected successfully');
        fetchIntegrations();
      } else {
        showToast('error', data.message);
      }
    } catch (err) {
      showToast('error', 'Failed to disconnect integration');
    } finally {
      setLoading(false);
    }
  };

  const handleInterpret = async (datasetId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/interpret/${datasetId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to interpret dataset');
      }

      const data = await response.json();
      setProphetData({
        type: 'interpretation',
        size: data.data.length,
        metrics: Object.keys(data.interpretation.metrics || {}),
        interpretation: data.interpretation
      });
      
      // Show success toast
      setToast({
        type: 'success',
        message: 'Dataset interpreted successfully'
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to interpret dataset');
    } finally {
      setLoading(false);
    }
  };

  const exportToTableau = async (sessionId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/export/tableau`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        showToast('success', 'Export completed successfully');
        window.location.href = data.filepath;
      } else {
        showToast('error', data.message);
      }
    } catch (err) {
      showToast('error', 'Failed to export to Tableau');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = async (sessionId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/export/pdf/${sessionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate PDF report');
      }
      
      const data = await response.json();
      
      // Create a temporary link to download the file
      const link = document.createElement('a');
      link.href = data.file_path;
      link.download = `scroll_report_${sessionId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setToast({
        type: 'success',
        message: 'PDF report generated successfully'
      });
    } catch (error) {
      setToast({
        type: 'error',
        message: error instanceof Error ? error.message : 'Failed to generate PDF report'
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePushToGitHub = async (sessionId: string, repoName: string, commitMessage: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/export/github/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          repo_name: repoName,
          commit_message: commitMessage
        })
      });

      if (!response.ok) {
        throw new Error('Failed to push to GitHub');
      }

      const data = await response.json();
      
      setToast({
        type: 'success',
        message: 'Successfully pushed to GitHub'
      });

      // Open commit URL in new tab
      window.open(data.commit_url, '_blank');
      
      // Close modal
      setSelectedSessionForGitHub(null);
      
      // Refresh sessions
      fetchSessions();
    } catch (error) {
      setToast({
        type: 'error',
        message: error instanceof Error ? error.message : 'Failed to push to GitHub'
      });
    } finally {
      setLoading(false);
    }
  };

  const triggerSync = async (source?: string) => {
    setSyncing(true);
    try {
      const url = source 
        ? `http://localhost:8000/api/sync/trigger/${source}`
        : 'http://localhost:8000/api/sync/trigger';
        
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Sync failed');
      }
      
      toast.success('Sync triggered successfully');
      await fetchSyncStatus();
    } catch (error) {
      toast.error('Failed to trigger sync');
      console.error('Error triggering sync:', error);
    } finally {
      setSyncing(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#f5222d' }} />;
      case 'syncing':
        return <SyncOutlined spin style={{ color: '#1890ff' }} />;
      default:
        return <CloudOutlined style={{ color: '#8c8c8c' }} />;
    }
  };

  const formatLastSync = (timestamp: string | null) => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleString();
  };

  const filteredSessions = sessions.filter(session =>
    session.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
    session.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column - Integrations */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>
                <ScrollGold>Connected Integrations</ScrollGold>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {integrations.map((integration) => (
                  <div key={integration.id} className="border rounded p-4">
                    <h3 className="font-semibold">{integration.name}</h3>
                    <p className="text-sm text-gray-600">{integration.type}</p>
                    <div className="mt-2">
                      {integration.status === 'connected' ? (
                        <Button
                          variant="destructive"
                          onClick={() => disconnectIntegration(integration.id)}
                          disabled={loading}
                        >
                          Disconnect
                        </Button>
                      ) : (
                        <Button
                          onClick={() => setSelectedIntegration(integration.id)}
                          disabled={loading}
                        >
                          Connect
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>
                <ScrollGold>Available Datasets</ScrollGold>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {datasets.map((dataset) => (
                  <div key={dataset.id} className="border rounded p-4">
                    <h3 className="font-semibold">{dataset.name}</h3>
                    <p className="text-sm text-gray-600">
                      {dataset.source} • {dataset.type}
                    </p>
                    <p className="text-xs text-gray-500">
                      Last updated: {new Date(dataset.lastUpdated).toLocaleString()}
                    </p>
                    <div className="mt-2">
                      <Button
                        onClick={() => handleInterpret(dataset.id)}
                        disabled={loading}
                      >
                        Interpret
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Cloud Sync Card */}
          <Card>
            <CardHeader>
              <CardTitle>
                <ScrollGold>Cloud Sync</ScrollGold>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Button
                    onClick={() => triggerSync()}
                    disabled={syncing}
                    className="w-full"
                  >
                    <SyncOutlined />
                    {syncing ? 'Syncing...' : 'Sync All Sources'}
                  </Button>
                </div>

                {syncStatus && (
                  <>
                    <Alert
                      message="Dropbox"
                      description={
                        <Space>
                          {getStatusIcon(syncStatus.dropbox.status)}
                          <Text>Last sync: {formatLastSync(syncStatus.dropbox.last_sync)}</Text>
                          <Button 
                            size="small" 
                            onClick={() => triggerSync('dropbox')}
                            loading={syncing}
                          >
                            Sync Now
                          </Button>
                        </Space>
                      }
                      type={syncStatus.dropbox.status === 'error' ? 'error' : 'info'}
                    />
                    
                    <Alert
                      message="Google Drive"
                      description={
                        <Space>
                          {getStatusIcon(syncStatus.gdrive.status)}
                          <Text>Last sync: {formatLastSync(syncStatus.gdrive.last_sync)}</Text>
                          <Button 
                            size="small" 
                            onClick={() => triggerSync('gdrive')}
                            loading={syncing}
                          >
                            Sync Now
                          </Button>
                        </Space>
                      }
                      type={syncStatus.gdrive.status === 'error' ? 'error' : 'info'}
                    />
                    
                    <Alert
                      message="OneDrive"
                      description={
                        <Space>
                          {getStatusIcon(syncStatus.onedrive.status)}
                          <Text>Last sync: {formatLastSync(syncStatus.onedrive.last_sync)}</Text>
                          <Button 
                            size="small" 
                            onClick={() => triggerSync('onedrive')}
                            loading={syncing}
                          >
                            Sync Now
                          </Button>
                        </Space>
                      }
                      type={syncStatus.onedrive.status === 'error' ? 'error' : 'info'}
                    />
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Middle column - Sessions */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>
                <ScrollGold>Recent Sessions</ScrollGold>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Input
                    type="search"
                    placeholder="Search sessions..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                {filteredSessions.map((session) => (
                  <div key={session.id} className="bg-white p-4 rounded-lg shadow">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium">{session.domain}</h3>
                        <p className="text-sm text-gray-500">
                          {new Date(session.timestamp).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleExportPDF(session.id)}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Export PDF
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedSessionForGitHub(session.id)}
                        >
                          <Github className="w-4 h-4 mr-2" />
                          Push to GitHub
                        </Button>
                      </div>
                    </div>
                    <p className="mt-2 text-sm">{session.interpretation.caption}</p>
                    {session.github_commit_url && (
                      <a
                        href={session.github_commit_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-500 hover:underline mt-2 block"
                      >
                        View on GitHub
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right column - ScrollProphet */}
        <div className="space-y-6">
          <ScrollProphet
            context={prophetContext}
            data={prophetData}
          />
        </div>
      </div>

      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Loading size="lg" />
        </div>
      )}

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}

      {/* Integration Connection Modal */}
      {selectedIntegration && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Connect Integration</CardTitle>
            </CardHeader>
            <CardContent>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.currentTarget);
                  const credentials = Object.fromEntries(formData.entries());
                  connectIntegration(selectedIntegration, credentials);
                  setSelectedIntegration(null);
                }}
                className="space-y-4"
              >
                {integrations
                  .find((i) => i.id === selectedIntegration)
                  ?.credentials?.map((field) => (
                    <div key={field}>
                      <Label htmlFor={field}>{field}</Label>
                      <Input
                        type="password"
                        id={field}
                        name={field}
                        required
                      />
                    </div>
                  ))}
                <div className="flex justify-end space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setSelectedIntegration(null)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={loading}>
                    Connect
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* GitHub Export Modal */}
      <GitHubExportModal
        isOpen={!!selectedSessionForGitHub}
        onClose={() => setSelectedSessionForGitHub(null)}
        onSubmit={(repoName, commitMessage) => {
          if (selectedSessionForGitHub) {
            handlePushToGitHub(selectedSessionForGitHub, repoName, commitMessage);
          }
        }}
        loading={loading}
      />
    </div>
  );
};

export default IntegrationDashboard; 