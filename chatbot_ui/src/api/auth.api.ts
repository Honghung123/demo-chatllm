import { LoginRequest } from "@/types/auth.type";
import axios from "axios";

export const handleLogin = async (username: string, password: string) => {
	const request: LoginRequest = {
		username: username,
		password: password,
	};
	// const response = await axios.post<LoginResponse>("/api/auth/login", request)
	const response = {
		data: {
			id: 1,
			username: "username",
			name: "Name",
			role: "admin",
		},
	};

	return response.data;
};
