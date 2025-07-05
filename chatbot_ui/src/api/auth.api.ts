import myAxios from "@/api/axios";
import { LoginRequest, LoginResponse } from "@/types/auth.type";
import { RoleType } from "@/types/user.type";

export const handleLogin = async (username: string, password: string) => {
	const request: LoginRequest = {
		username: username,
		password: password,
	};
	const response = await myAxios.post<LoginResponse>("/login", request);
	if ([200, 201, 204].includes(response.status)) {
		return response.data;
	} else {
		return null;
	}
};

export const getAllRoles = async () => {
	const response = await myAxios.get<RoleType[]>("/roles");
	if ([200, 201, 204].includes(response.status)) {
		return response.data;
	} else {
		return [];
	}
};
