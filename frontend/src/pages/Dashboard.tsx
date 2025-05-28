import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert
} from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import axiosInstance from '../utils/axios';

interface ScrollData {
  id: string;
  content: string;
  timestamp: string;
  status: string;
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [scrolls, setScrolls] = useState<ScrollData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchScrolls();
  }, []);

  const fetchScrolls = async () => {
    try {
      const response = await axiosInstance.get('/api/scrolls');
      setScrolls(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch scrolls');
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography component="h1" variant="h4">
                Welcome, {user?.username}!
              </Typography>
              <Button variant="outlined" color="primary" onClick={handleLogout}>
                Logout
              </Button>
            </Box>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            <Typography variant="h6" gutterBottom>
              Recent Scrolls
            </Typography>
            {scrolls.length === 0 ? (
              <Typography color="textSecondary">No scrolls found</Typography>
            ) : (
              <Grid container spacing={2}>
                {scrolls.map((scroll) => (
                  <Grid item xs={12} key={scroll.id}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="subtitle1">{scroll.content}</Typography>
                      <Typography variant="body2" color="textSecondary">
                        {new Date(scroll.timestamp).toLocaleString()}
                      </Typography>
                      <Typography
                        variant="body2"
                        color={scroll.status === 'completed' ? 'success.main' : 'warning.main'}
                      >
                        Status: {scroll.status}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 