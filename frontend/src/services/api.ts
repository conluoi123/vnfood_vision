import axios from 'axios';

// Dùng đường dẫn tương đối (đã cấu hình qua Vite Proxy) để Ngrok có thể hoạt động được
const API_URL = '/api/v1';

export const analyzeFoodImage = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_URL}/predict/image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error("Lỗi khi gọi API Backend:", error);
    throw error;
  }
};
