import React, { useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Environment, Float, MeshDistortMaterial, ScrollControls, useScroll } from "@react-three/drei";
import { motion } from "framer-motion";
import { SignInButton, SignUpButton, useUser } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import * as THREE from "three";
import { useTheme } from "../hooks/useTheme";

// ── 3D Scene ──────────────────────────────────────────────────────────────────

function AbstractShape({ theme }) {
  const meshRef = useRef();
  const innerRef = useRef();

  const outerColor = theme === "dark" ? "#0369a1" : "#0ea5e9";
  const innerColor = theme === "dark" ? "#0891b2" : "#06b6d4";
  const ringColor  = theme === "dark" ? "#0284c7" : "#38bdf8";

  useFrame((state, delta) => {
    meshRef.current.rotation.x += delta * 0.08;
    meshRef.current.rotation.y += delta * 0.12;
    innerRef.current.rotation.x -= delta * 0.05;
    innerRef.current.rotation.z += delta * 0.07;
  });

  return (
    <Float speed={1.8} rotationIntensity={0.6} floatIntensity={1.2}>
      {/* Outer wireframe */}
      <mesh ref={meshRef} scale={2.0}>
        <icosahedronGeometry args={[1, 1]} />
        <meshStandardMaterial color={outerColor} wireframe opacity={0.35} transparent />
      </mesh>
      {/* Inner distorted sphere */}
      <mesh ref={innerRef} scale={1.1}>
        <sphereGeometry args={[1, 64, 64]} />
        <MeshDistortMaterial
          color={innerColor}
          envMapIntensity={1.2}
          clearcoat={1}
          clearcoatRoughness={0}
          metalness={0.6}
          roughness={0.05}
          distort={0.35}
          speed={2.5}
          opacity={0.85}
          transparent
        />
      </mesh>
      {/* Accent ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]} scale={1.9}>
        <torusGeometry args={[1, 0.018, 16, 100]} />
        <meshStandardMaterial color={ringColor} opacity={0.5} transparent />
      </mesh>
    </Float>
  );
}

function ScrollCamera() {
  const scroll = useScroll();
  const { camera } = useThree();
  const target = useRef(new THREE.Vector3(0, 0, 5));

  useFrame(() => {
    const t = scroll.offset; // 0 → 1
    // Move camera back + shift up as user scrolls
    target.current.set(0, -t * 3, 5 + t * 2);
    camera.position.lerp(target.current, 0.06);
    camera.lookAt(0, -t * 1.5, 0);
  });

  return null;
}

// ── Landing Page ──────────────────────────────────────────────────────────────

const features = [
  {
    icon: "🧠",
    title: "Intent Extraction",
    desc: "Every message is parsed for intent before execution. Nothing passes through raw.",
    color: "from-violet-400 to-purple-500",
    bg: "bg-violet-50 dark:bg-violet-900/10",
    border: "border-violet-200 dark:border-violet-500/20",
  },
  {
    icon: "⚖️",
    title: "Policy Engine",
    desc: "A rule-based policy layer evaluates risk level and grants or denies tool access.",
    color: "from-cyan-400 to-teal-500",
    bg: "bg-cyan-50 dark:bg-cyan-900/10",
    border: "border-cyan-200 dark:border-cyan-500/20",
  },
  {
    icon: "🛡️",
    title: "Decision Guard",
    desc: "Multi-step decision routing ensures only authorised actions reach external APIs.",
    color: "from-pink-400 to-rose-500",
    bg: "bg-pink-50 dark:bg-pink-900/10",
    border: "border-pink-200 dark:border-pink-500/20",
  },
  {
    icon: "📋",
    title: "Audit Trail",
    desc: "Every interaction is logged with full metadata: intent, risk, decision, and tool.",
    color: "from-amber-400 to-orange-500",
    bg: "bg-amber-50 dark:bg-amber-900/10",
    border: "border-amber-200 dark:border-amber-500/20",
  },
];

const securityPoints = [
  { icon: "🔒", label: "Trusted tool access" },
  { icon: "🚫", label: "Prompt injection blocked" },
  { icon: "🔑", label: "OAuth via Clerk" },
  { icon: "📊", label: "Live risk scoring" },
  { icon: "🌐", label: "Finnhub + Tavily APIs" },
  { icon: "🤖", label: "LLM guardrail layer" },
];

function HeroContent({ isSignedIn, navigate, theme }) {
  return (
    <div className="w-full" style={{ height: "300vh" }}>
      {/* ── Section 1: Hero ── */}
      <div
        className="h-screen flex flex-col items-center justify-center text-center px-6 pt-20"
        id="hero"
      >
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, ease: "easeOut" }}
          className="max-w-4xl"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-cyan-300 dark:border-cyan-500/30 bg-cyan-50/80 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 text-xs font-bold mb-8 uppercase tracking-widest backdrop-blur-md shadow-sm">
            <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
            Enterprise-Grade AI Safety
          </div>

          <h1 className="font-display text-5xl md:text-7xl font-bold leading-tight mb-6 text-slate-900 dark:text-white">
            Financial AI,{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-violet-600">
              Guarded by Design.
            </span>
          </h1>

          <p className="text-lg md:text-xl text-slate-500 dark:text-slate-400 mb-10 max-w-2xl mx-auto font-light leading-relaxed">
            IntentShield intercepts every interaction, enforcing strict policy guardrails before
            your data ever touches an external API or automated agent.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            {isSignedIn ? (
              <button
                onClick={() => navigate("/app")}
                className="px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-bold text-base transition-all shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:-translate-y-1"
              >
                Access Terminal
              </button>
            ) : (
              <SignUpButton mode="modal">
                <button className="px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-bold text-base transition-all shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:-translate-y-1">
                  Start Building Safe AI
                </button>
              </SignUpButton>
            )}
            <a
              href="#features"
              className="px-8 py-4 rounded-full border border-slate-300 dark:border-white/10 bg-white/70 dark:bg-white/5 hover:bg-white dark:hover:bg-white/10 hover:border-slate-400 text-slate-700 dark:text-slate-300 font-bold text-base transition-all backdrop-blur-sm shadow-sm"
            >
              Explore Features
            </a>
          </div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8, duration: 1 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-cyan-500"
        >
          <span className="text-xs uppercase tracking-widest font-semibold">Scroll to explore</span>
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
            className="w-px h-12 bg-gradient-to-b from-cyan-500/80 to-transparent"
          />
        </motion.div>
      </div>

      {/* ── Section 2: Features ── */}
      <div className="h-screen flex flex-col items-center justify-center px-6" id="features">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.7 }}
          className="text-center mb-12"
        >
          <h2 className="font-display text-4xl md:text-5xl font-bold text-slate-900 dark:text-white mb-4">
            Built for{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-violet-600">
              Secure Intelligence
            </span>
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-lg max-w-xl mx-auto">
            A multi-layered pipeline that ensures every AI action is intentional, authorised, and
            auditable.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 max-w-5xl w-full">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className={`${f.bg} ${f.border} border rounded-2xl p-5 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300`}
            >
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center text-xl mb-3 shadow-sm`}>
                {f.icon}
              </div>
              <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100 mb-1.5">{f.title}</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* ── Section 3: Security ── */}
      <div className="h-screen flex flex-col items-center justify-center px-6" id="security">
        <div className="max-w-4xl w-full grid md:grid-cols-2 gap-12 items-center">
          {/* Left */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-100 dark:bg-violet-900/10 border border-violet-200 dark:border-violet-500/20 text-violet-700 dark:text-violet-400 text-xs font-bold mb-5 uppercase tracking-wider">
              🔐 Trusted Security
            </div>
            <h2 className="font-display text-4xl font-bold text-slate-900 dark:text-white mb-5 leading-tight">
              Every action is{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-500 to-pink-500">
                policy-governed.
              </span>
            </h2>
            <p className="text-slate-500 dark:text-slate-400 text-base leading-relaxed mb-6">
              IntentShield wraps your LLM with a hard enforcement layer. No tool call happens
              without explicit policy clearance — no exceptions.
            </p>
            {isSignedIn ? (
              <button
                onClick={() => navigate("/app")}
                className="px-6 py-3 rounded-full bg-gradient-to-r from-violet-500 to-pink-500 text-white font-bold text-sm shadow-lg shadow-violet-500/25 hover:-translate-y-1 transition-all"
              >
                Open Dashboard →
              </button>
            ) : (
              <SignUpButton mode="modal">
                <button className="px-6 py-3 rounded-full bg-gradient-to-r from-violet-500 to-pink-500 text-white font-bold text-sm shadow-lg shadow-violet-500/25 hover:-translate-y-1 transition-all">
                  Get Started Free →
                </button>
              </SignUpButton>
            )}
          </motion.div>

          {/* Right: security grid */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="grid grid-cols-2 gap-4"
          >
            {securityPoints.map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
                className="glass rounded-2xl p-4 flex items-center gap-3 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200"
              >
                <span className="text-xl">{s.icon}</span>
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-200">{s.label}</span>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* Footer strip */}
        <div className="mt-16 text-xs text-slate-400 text-center">
          © 2026 IntentShield
        </div>
      </div>
    </div>
  );
}

// ── Root Export ───────────────────────────────────────────────────────────────

export default function LandingPage() {
  const { isSignedIn } = useUser();
  const navigate = useNavigate();
  const [theme, toggleTheme] = useTheme();

  return (
    <div className="relative w-full min-h-screen transition-colors duration-500 overflow-x-hidden">
      {/* Fixed 3D Canvas (acts as background for entire page) */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <Canvas camera={{ position: [0, 0, 5] }}>
          <ScrollControls pages={3} damping={0.15}>
            <ambientLight intensity={0.7} />
            <directionalLight position={[10, 10, 5]} intensity={1.5} />
            <pointLight position={[-10, -10, -5]} intensity={0.5} color="#7c3aed" />
            <Environment preset="city" />
            <AbstractShape theme={theme} />
            <ScrollCamera />
          </ScrollControls>
        </Canvas>
      </div>

      {/* Soft mesh overlay so text remains readable */}
      <div className="fixed inset-0 z-0 pointer-events-none bg-gradient-to-br from-white/75 via-cyan-50/60 to-violet-50/70 dark:from-slate-950/80 dark:via-slate-900/40 dark:to-slate-950/80 backdrop-blur-[2px] transition-colors duration-500" />

      {/* Navigation */}
      <nav className="fixed top-0 w-full px-6 py-4 z-30 flex justify-between items-center">
        <div className="flex items-center gap-2 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border border-white/80 dark:border-white/10 rounded-2xl px-4 py-2.5 shadow-sm transition-colors">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center text-base shadow-sm">
            🛡️
          </div>
          <span className="font-display font-bold text-lg tracking-wide text-slate-900 dark:text-white">IntentShield</span>
        </div>

        <div className="hidden md:flex items-center gap-1 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border border-white/80 dark:border-white/10 rounded-2xl px-2 py-2 shadow-sm transition-colors">
          <a href="#features" className="px-4 py-1.5 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-slate-100/80 dark:hover:bg-white/10 hover:text-slate-900 dark:hover:text-white text-sm font-medium transition-colors">Features</a>
          <a href="#security" className="px-4 py-1.5 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-slate-100/80 dark:hover:bg-white/10 hover:text-slate-900 dark:hover:text-white text-sm font-medium transition-colors">Security</a>
        </div>

        <div className="flex gap-2 items-center">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border border-white/80 dark:border-white/10 text-slate-500 dark:text-slate-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-all shadow-sm"
            title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          >
            {theme === "dark" ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.364 17.636l-.707.707M6.364 6.364l.707.707m11.314 11.314l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>

          {isSignedIn ? (
            <button
              onClick={() => navigate("/app")}
              className="px-5 py-2.5 rounded-full bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-semibold text-sm transition-all shadow-md shadow-cyan-500/20 hover:-translate-y-0.5"
            >
              Dashboard
            </button>
          ) : (
            <>
              <SignInButton mode="modal">
                <button className="px-5 py-2.5 rounded-full text-slate-700 dark:text-slate-200 bg-white/60 dark:bg-white/5 backdrop-blur-sm hover:bg-white dark:hover:bg-white/10 border border-white/80 dark:border-white/10 font-semibold text-sm transition-all shadow-sm">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="px-5 py-2.5 rounded-full bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-semibold text-sm transition-all shadow-md shadow-cyan-500/20 hover:-translate-y-0.5">
                  Get Started
                </button>
              </SignUpButton>
            </>
          )}
        </div>
      </nav>

      {/* Scrollable HTML content on top */}
      <div className="relative z-10">
        <HeroContent isSignedIn={isSignedIn} navigate={navigate} theme={theme} />
      </div>
    </div>
  );
}
