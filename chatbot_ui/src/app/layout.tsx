import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en">
			<body className={`antialiased`}>
				{children}
				<Toaster />
			</body>
		</html>
	);
}
