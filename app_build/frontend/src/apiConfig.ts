const getApiBaseUrl = () => {
    const port = import.meta.env.VITE_API_PORT || '8400';
    return `http://localhost:${port}`;
};

export const API_BASE_URL = getApiBaseUrl();
