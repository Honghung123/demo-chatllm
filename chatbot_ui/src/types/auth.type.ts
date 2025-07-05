export type LoginRequest = {
	username: string;
	password: string;
};

export type LoginResponse = {
	id: string;
	username: string;
	name: string;
	role: string;
};
