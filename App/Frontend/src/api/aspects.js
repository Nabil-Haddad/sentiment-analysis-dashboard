import client from './client';

export const getAspects = () =>
  client.get('/aspects/');

export const addAspect = (name) =>
  client.post('/aspects/', { name });

export const toggleAspect = (id, is_active) =>
  client.patch(`/aspects/${id}`, { is_active });

export const deleteAspect = (id) =>
  client.delete(`/aspects/${id}`);
