import axios from "axios";

const myAxios = axios.create({
	baseURL: process.env.NEXT_PUBLIC_BASE_URL,
});
// Add a request interceptor
myAxios.interceptors.request.use((config) => config);
// Add a response interceptor
myAxios.interceptors.response.use(
	(response) => response,
	async (error) => {
		return Promise.reject(error);
	}
);

export default myAxios;
