"use client";

import { handleLogin } from "@/api/auth.api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AlertCircle, Eye, EyeOff } from "lucide-react";
import { useRouter } from "next/navigation";
import type React from "react";
import { useState } from "react";

export default function LoginPage() {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [showPassword, setShowPassword] = useState(false);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState("");
	const router = useRouter();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setIsLoading(true);
		setError("");

		try {
			const response = await handleLogin(username, password);
			sessionStorage.setItem("user", JSON.stringify(response));
			// Navigate to /chat
			router.push("/chat");
		} catch (err: any) {
			setError(err.response?.data?.message || "Login failed. Please try again.");
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<div className="min-h-screen bg-white flex items-center justify-center p-4">
			<div className="w-full max-w-md">
				<Card className="bg-white border border-gray-200 shadow-lg">
					<CardHeader className="space-y-1 text-center">
						<CardTitle className="text-2xl font-semibold text-black">Welcome back</CardTitle>
					</CardHeader>
					<CardContent className="space-y-4">
						<form onSubmit={handleSubmit} className="space-y-4">
							{error && (
								<div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-md border border-red-200">
									<AlertCircle className="h-4 w-4" />
									<span className="text-sm">{error}</span>
								</div>
							)}

							<div className="space-y-2">
								<Label htmlFor="username" className="text-black text-sm font-medium">
									Username
								</Label>
								<Input
									id="username"
									type="text"
									placeholder="Enter your username"
									value={username}
									onChange={(e) => setUsername(e.target.value)}
									className="bg-white border-gray-300 text-black placeholder:text-gray-400 focus:border-black focus:ring-black h-12"
									required
								/>
							</div>

							<div className="space-y-2">
								<Label htmlFor="password" className="text-black text-sm font-medium">
									Password
								</Label>
								<div className="relative">
									<Input
										id="password"
										type={showPassword ? "text" : "password"}
										placeholder="Enter your password"
										value={password}
										onChange={(e) => setPassword(e.target.value)}
										className="bg-white border-gray-300 text-black placeholder:text-gray-400 focus:border-black focus:ring-black h-12 pr-10"
										required
									/>
									<button
										type="button"
										onClick={() => setShowPassword(!showPassword)}
										className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-black transition-colors"
									>
										{showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
									</button>
								</div>
							</div>

							<Button
								type="submit"
								disabled={isLoading}
								className="w-full h-12 bg-black hover:bg-gray-800 cursor-pointer text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
							>
								{isLoading ? (
									<div className="flex items-center space-x-2">
										<div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
										<span>Signing in...</span>
									</div>
								) : (
									"Sign in"
								)}
							</Button>
						</form>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
