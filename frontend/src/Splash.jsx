import React, { useEffect } from "react";
import { motion } from "framer-motion";

export default function Splash({ onFinish }) {
  useEffect(() => {
    const timer = setTimeout(onFinish, 2200);
    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden font-poppins">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-pink-500 to-yellow-500 animate-gradient-x opacity-90"></div>

      {/* Logo + Title */}
      <motion.div
        className="relative z-10 text-center"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1, ease: "easeOut" }}
      >
        <h1 className="text-6xl font-extrabold text-white drop-shadow-lg tracking-tight">
          NoteMate
        </h1>
        <p className="mt-4 text-lg text-white/90 font-light tracking-wide">
          Transcribe • Summarize • Understand
        </p>
      </motion.div>
    </div>
  );
}
