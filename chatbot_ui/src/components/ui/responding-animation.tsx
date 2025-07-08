"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface RespondingAnimationProps {
	className?: string;
	variant?: "dots" | "pulse" | "shimmer" | "wave" | "typing" | "gradient";
}

export function RespondingAnimation({ className, variant = "dots" }: RespondingAnimationProps) {
	const [dotCount, setDotCount] = useState(1);

	useEffect(() => {
		if (variant === "dots" || variant === "typing") {
			const interval = setInterval(() => {
				setDotCount((prev) => (prev >= 3 ? 1 : prev + 1));
			}, 300);
			return () => clearInterval(interval);
		}
	}, [variant]);

	const renderDots = () => {
		return Array.from({ length: 3 }, (_, i) => (
			<span
				key={i}
				className={cn(
					"inline-block w-1 h-1 bg-current rounded-full transition-opacity duration-200",
					i < dotCount ? "opacity-100" : "opacity-30"
				)}
			/>
		));
	};

	const variants = {
		dots: (
			<div
				className={cn(
					"flex-1 flex items-baseline space-x-1 bg-gradient-to-r from-gray-400 via-gray-600 to-gray-400 bg-clip-text text-transparent animate-pulse bg-[length:200%_100%] animate-shimmer",
					className
				)}
			>
				<span>Responding</span>
				<div className="flex space-x-1">{renderDots()}</div>
			</div>
		),

		pulse: (
			<div className={cn("flex-1 flex items-center", className)}>
				<span className="animate-pulse">Responding...</span>
			</div>
		),

		shimmer: (
			<div className={cn("flex-1 flex items-center", className)}>
				<span className="bg-gradient-to-r from-gray-400 via-gray-600 to-gray-400 bg-clip-text text-transparent animate-pulse bg-[length:200%_100%] animate-shimmer">
					Responding...
				</span>
			</div>
		),

		wave: (
			<div className={cn("flex-1 flex items-center", className)}>
				<div className="flex">
					{"Responding...".split("").map((char, i) => (
						<span
							key={i}
							className="animate-wave inline-block"
							style={{
								animationDelay: `${i * 0.1}s`,
							}}
						>
							{char === " " ? "\u00A0" : char}
						</span>
					))}
				</div>
			</div>
		),

		typing: (
			<div className={cn("flex-1 flex items-center space-x-2", className)}>
				<span>Responding</span>
				<div className="flex space-x-1">
					{Array.from({ length: 3 }, (_, i) => (
						<div
							key={i}
							className={cn("w-2 h-2 bg-gray-500 rounded-full animate-bounce")}
							style={{
								animationDelay: `${i * 0.2}s`,
								animationDuration: "1s",
							}}
						/>
					))}
				</div>
			</div>
		),

		gradient: (
			<div className={cn("flex-1 flex items-center", className)}>
				<span className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent animate-gradient-x bg-[length:200%_200%]">
					Responding...
				</span>
			</div>
		),
	};

	return variants[variant];
}
