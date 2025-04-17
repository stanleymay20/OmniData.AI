import React, { useState, useCallback } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Paper,
  Grid,
  CircularProgress,
  Alert,
} from '@mui/material';
import { DropzoneArea } from 'mui-file-upload';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  ResponsiveContainer,
} from 'recharts';
import { DataGrid } from '@mui/x-data-grid';

const steps = [
  'Upload Data',
  'Data Profiling',
  'Configure Model',
  'Training Results',
];

interface DataProfile {
  shape: [number, number];
  columns: string[];
  dtypes: { [key: string]: string };
  missing_values: { [key: string]: number };
  numeric_stats: {
    [key: string]: {
      mean: number;
      std: number;
      min: number;
      max: number;
      quartiles: { [key: string]: number };
    };
  };
  categorical_stats: {
    [key: string]: {
      unique_values: number;
      top_values: { [key: string]: number };
    };
  };
}

interface ModelResults {
  model_type: string;
  parameters: { [key: string]: any };
  metrics: { [key: string]: number };
  feature_importance: Array<{ feature: string; importance: number }>;
}

export default function AutoMLDashboard() {
  const [activeStep, setActiveStep] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [dataProfile, setDataProfile] = useState<DataProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelConfig, setModelConfig] = useState({
    target_column: '',
    task_type: 'classification',
    auto_optimize: true,
  });
  const [modelResults, setModelResults] = useState<ModelResults | null>(null);

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleFileChange = useCallback(async (files: File[]) => {
    if (files.length > 0) {
      setFile(files[0]);
      setLoading(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', files[0]);

      try {
        const response = await fetch('/api/automl/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to upload file');
        }

        const data = await response.json();
        setDataProfile(data.profile);
        handleNext();
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
  }, []);

  const handleTrainModel = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/automl/train', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(modelConfig),
      });

      if (!response.ok) {
        throw new Error('Failed to train model');
      }

      const results = await response.json();
      setModelResults(results);
      handleNext();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderUploadStep = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Upload your dataset (CSV or Parquet)
      </Typography>
      <DropzoneArea
        acceptedFiles={['.csv', '.parquet']}
        filesLimit={1}
        maxFileSize={50000000}
        onChange={handleFileChange}
        showFileNames
        showPreviewsInDropzone={false}
        useChipsForPreview
        dropzoneText="Drag and drop a file here or click to browse"
      />
    </Box>
  );

  const renderDataProfile = () => {
    if (!dataProfile) return null;

    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Data Profile
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">Dataset Overview</Typography>
              <Typography>
                Rows: {dataProfile.shape[0]}
                <br />
                Columns: {dataProfile.shape[1]}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">Missing Values</Typography>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart
                  data={Object.entries(dataProfile.missing_values).map(
                    ([column, count]) => ({
                      column,
                      count,
                    })
                  )}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="column" angle={45} textAnchor="end" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">Column Details</Typography>
              <DataGrid
                rows={dataProfile.columns.map((column, index) => ({
                  id: index,
                  column,
                  type: dataProfile.dtypes[column],
                  missing: dataProfile.missing_values[column],
                }))}
                columns={[
                  { field: 'column', headerName: 'Column', flex: 1 },
                  { field: 'type', headerName: 'Type', flex: 1 },
                  { field: 'missing', headerName: 'Missing Values', flex: 1 },
                ]}
                autoHeight
                pageSize={5}
              />
            </Paper>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderModelConfig = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Configure Model
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            {/* Add model configuration form here */}
          </Paper>
        </Grid>
      </Grid>
      <Box sx={{ mt: 3 }}>
        <Button
          variant="contained"
          onClick={handleTrainModel}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Train Model'}
        </Button>
      </Box>
    </Box>
  );

  const renderResults = () => {
    if (!modelResults) return null;

    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Model Results
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">Model Metrics</Typography>
              <DataGrid
                rows={Object.entries(modelResults.metrics).map(
                  ([metric, value], index) => ({
                    id: index,
                    metric,
                    value: typeof value === 'number' ? value.toFixed(4) : value,
                  })
                )}
                columns={[
                  { field: 'metric', headerName: 'Metric', flex: 1 },
                  { field: 'value', headerName: 'Value', flex: 1 },
                ]}
                autoHeight
                hideFooter
              />
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">Feature Importance</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={modelResults.feature_importance}
                  layout="vertical"
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis
                    dataKey="feature"
                    type="category"
                    width={150}
                  />
                  <Tooltip />
                  <Bar dataKey="importance" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return renderUploadStep();
      case 1:
        return renderDataProfile();
      case 2:
        return renderModelConfig();
      case 3:
        return renderResults();
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <Stepper activeStep={activeStep}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      <Box sx={{ mt: 2 }}>
        {getStepContent(activeStep)}
        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
          <Button
            color="inherit"
            disabled={activeStep === 0}
            onClick={handleBack}
            sx={{ mr: 1 }}
          >
            Back
          </Button>
          <Box sx={{ flex: '1 1 auto' }} />
          {activeStep !== steps.length - 1 && (
            <Button
              variant="contained"
              onClick={handleNext}
              disabled={
                (activeStep === 0 && !file) ||
                (activeStep === 2 && !modelConfig.target_column)
              }
            >
              Next
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
} 