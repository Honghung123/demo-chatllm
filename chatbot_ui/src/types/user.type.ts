export enum RoleName {
	USER = "user",
	ADMIN = "admin",
}

export type RoleType = {
	id: string;
	displayName: string;
};

export type UserType = {
	id: string;
	username: string;
	name: string;
	role: string;
};
