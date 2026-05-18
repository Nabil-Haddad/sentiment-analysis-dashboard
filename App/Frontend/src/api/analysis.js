import client from './client';

export const submitAnalysis = (comments) =>
  client.post('/sentiment-analysis/', comments);

export const getAllAnalyses = () =>
  client.get('/sentiment-analysis/all');

export const getAnalysisResults = (id) =>
  client.get(`/sentiment-analysis/results/${id}`);

export const getSummary = () =>
  client.get('/sentiment-analysis/stats/summary');

export const deleteAnalysis = (id) =>
  client.delete(`/sentiment-analysis/${id}`);
