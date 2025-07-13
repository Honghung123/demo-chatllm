import React, { useEffect, useRef, useState } from "react";

interface TimerProps {
	isRunning: boolean; // biến boolean để điều khiển start/stop đồng hồ
}

const Timer: React.FC<TimerProps> = ({ isRunning }) => {
	const [secondsElapsed, setSecondsElapsed] = useState(0);
	const intervalRef = useRef<NodeJS.Timeout | null>(null);

	useEffect(() => {
		if (isRunning) {
			// Bắt đầu đếm thời gian
			intervalRef.current = setInterval(() => {
				setSecondsElapsed((prev) => prev + 1);
			}, 1000);
		} else {
			// Dừng đếm thời gian
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
				intervalRef.current = null;
			}
		}

		// Cleanup khi component unmount hoặc isRunning thay đổi
		return () => {
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
				intervalRef.current = null;
			}
		};
	}, [isRunning]);

	// Tính phút và giây từ tổng số giây đã đếm
	const minutes = Math.floor(secondsElapsed / 60);
	const seconds = secondsElapsed % 60;

	return (
		<span className="text-gray-700">
			{minutes.toString().padStart(2, "0")}:{seconds.toString().padStart(2, "0")}
		</span>
	);
};

export default Timer;
