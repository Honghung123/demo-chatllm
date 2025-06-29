import { cn } from "@/lib/utils";

interface LoadingCircleProps {
	size?: "sm" | "md" | "lg" | "xl";
	color?: "black" | "white" | "gray";
	className?: string;
	text?: string;
}

const sizeClasses = {
	sm: "w-4 h-4",
	md: "w-6 h-6",
	lg: "w-8 h-8",
	xl: "w-12 h-12",
};

const colorClasses = {
	black: "border-black border-t-transparent",
	white: "border-white border-t-transparent",
	gray: "border-gray-400 border-t-transparent",
};

export function LoadingCircle({ size = "md", color = "black", className, text }: LoadingCircleProps) {
	return (
		<div className={cn("flex flex-col items-center justify-center gap-2", className)}>
			<div className={cn("border-2 rounded-full animate-spin", sizeClasses[size], colorClasses[color])} />
			{text && (
				<span
					className={cn(
						"text-sm font-medium",
						color === "white" ? "text-white" : color === "gray" ? "text-gray-600" : "text-black"
					)}
				>
					{text}
				</span>
			)}
		</div>
	);
}

// Full page loading overlay
export function LoadingOverlay({ text = "Loading..." }: { text?: string }) {
	return (
		<div className="fixed inset-0 bg-white bg-opacity-80 flex items-center justify-center z-50">
			<LoadingCircle size="lg" text={text} />
		</div>
	);
}

// Inline loading for buttons
export function ButtonLoading({ size = "sm" }: { size?: "sm" | "md" }) {
	return <LoadingCircle size={size} color="white" className="inline-flex" />;
}
