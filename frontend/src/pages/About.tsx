export const About = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-6 text-center">
            About <span className="text-indigo-600">AgentVine</span>
          </h1>

          <div className="space-y-6">
            <div className="border-l-4 border-indigo-500 pl-4">
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">Application Name</h2>
              <p className="text-lg text-gray-600">AgentVine</p>
            </div>

            <div className="border-l-4 border-purple-500 pl-4">
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">Version</h2>
              <p className="text-lg text-gray-600">0.01</p>
            </div>

            <div className="border-l-4 border-pink-500 pl-4">
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">About the Platform</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                AgentVine is an innovative multi-agent platform designed to orchestrate and manage
                specialized AI agents. Each agent brings unique capabilities to solve specific problems,
                and together they form a powerful ecosystem that can tackle complex, multi-faceted challenges.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                Built with modern technologies including React, TypeScript, and FastAPI, AgentVine
                provides a robust foundation for developing scalable agent-based systems. The platform
                emphasizes clean architecture, type safety, and performance optimization.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Whether you're building customer service automation, content generation pipelines,
                or complex decision-making systems, AgentVine provides the tools and framework you
                need to bring your multi-agent vision to life.
              </p>
            </div>

            <div className="border-l-4 border-blue-500 pl-4">
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">Key Features</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>Modular agent architecture with specialized capabilities</li>
                <li>Real-time agent communication and coordination</li>
                <li>Type-safe API with comprehensive TypeScript support</li>
                <li>High-performance React frontend with Vite</li>
                <li>FastAPI backend for optimal performance</li>
                <li>Extensible plugin system for custom agents</li>
                <li>Production-ready with comprehensive testing</li>
                <li>Modern UI built with Tailwind CSS</li>
              </ul>
            </div>

            <div className="border-l-4 border-green-500 pl-4">
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">Technology Stack</h2>
              <div className="grid grid-cols-2 gap-4 text-gray-700">
                <div>
                  <h3 className="font-semibold text-indigo-600 mb-2">Frontend</h3>
                  <ul className="list-disc list-inside space-y-1">
                    <li>React 18+</li>
                    <li>TypeScript</li>
                    <li>Vite</li>
                    <li>TanStack Router</li>
                    <li>Tailwind CSS</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-purple-600 mb-2">Backend</h3>
                  <ul className="list-disc list-inside space-y-1">
                    <li>FastAPI</li>
                    <li>Python 3.11+</li>
                    <li>Pydantic</li>
                    <li>Pytest</li>
                    <li>RESTful API</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200 text-center">
            <p className="text-gray-500 text-sm">
              Built with care by the AgentVine team
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
