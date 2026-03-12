import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <h1 className="mb-4 text-4xl font-bold">VerseFina</h1>
      <p className="mb-8 text-xl text-gray-600">Agent-native finance world.</p>
      <Link href="/onboarding" className="rounded-lg bg-blue-600 px-6 py-3 text-white">
        开始接入
      </Link>
    </div>
  );
}
