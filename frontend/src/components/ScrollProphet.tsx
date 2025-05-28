import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loading } from '@/components/ui/loading';
import { Toast } from '@/components/ui/toast';
import { ScrollGold } from '@/components/ui/scroll-gold';
import { useAuth } from '@/auth/AuthContext';

interface Insight {
  key_insights: string[];
  analysis_areas: string[];
  visualizations: string[];
  action_items: string[];
}

interface ScrollProphetProps {
  context?: Record<string, any>;
  data?: Record<string, any>;
}

const ScrollProphet: React.FC<ScrollProphetProps> = ({ context, data }) => {
  const { token } = useAuth();
  const [insights, setInsights] = useState<Insight | null>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'insights' | 'recommendations'>('insights');

  useEffect(() => {
    if (context) {
      fetchInsights();
    }
    if (data) {
      fetchRecommendations();
    }
  }, [context, data]);

  const fetchInsights = async () => {
    if (!context) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/prophet/insights', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ context })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch insights');
      }

      const data = await response.json();
      setInsights(data.insights);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch insights');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    if (!data) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/prophet/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ data })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      const responseData = await response.json();
      setRecommendations(responseData.recommendations);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  };

  const renderInsights = () => {
    if (!insights) return null;

    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-2">Key Insights</h3>
          <ul className="list-disc pl-5 space-y-1">
            {insights.key_insights.map((insight, index) => (
              <li key={index} className="text-gray-700">{insight}</li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-2">Analysis Areas</h3>
          <ul className="list-disc pl-5 space-y-1">
            {insights.analysis_areas.map((area, index) => (
              <li key={index} className="text-gray-700">{area}</li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-2">Recommended Visualizations</h3>
          <ul className="list-disc pl-5 space-y-1">
            {insights.visualizations.map((viz, index) => (
              <li key={index} className="text-gray-700">{viz}</li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-2">Action Items</h3>
          <ul className="list-disc pl-5 space-y-1">
            {insights.action_items.map((action, index) => (
              <li key={index} className="text-gray-700">{action}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  const renderRecommendations = () => {
    if (!recommendations.length) return null;

    return (
      <div className="space-y-4">
        <ul className="list-disc pl-5 space-y-2">
          {recommendations.map((recommendation, index) => (
            <li key={index} className="text-gray-700">{recommendation}</li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <ScrollGold>ScrollProphet AI Assistant</ScrollGold>
          <div className="flex space-x-2">
            <Button
              variant={activeTab === 'insights' ? 'default' : 'outline'}
              onClick={() => setActiveTab('insights')}
              disabled={!context}
            >
              Insights
            </Button>
            <Button
              variant={activeTab === 'recommendations' ? 'default' : 'outline'}
              onClick={() => setActiveTab('recommendations')}
              disabled={!data}
            >
              Recommendations
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8">
            <Loading size="lg" />
          </div>
        ) : (
          <div className="py-4">
            {activeTab === 'insights' ? renderInsights() : renderRecommendations()}
          </div>
        )}
      </CardContent>

      {error && (
        <Toast
          type="error"
          message={error}
          onClose={() => setError(null)}
        />
      )}
    </Card>
  );
};

export default ScrollProphet; 