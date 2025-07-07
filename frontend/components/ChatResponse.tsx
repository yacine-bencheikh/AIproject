// components/ChatResponse.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';

interface Source {
    source: string;
    title: string;
    page: number;
}

interface ChatResponseProps {
    response: string; // Raw markdown response
    sources: Source[];
}

const ChatResponse: React.FC<ChatResponseProps> = ({ response, sources }) => {
    // Parse markdown sections
    const sections = response.split(/\d+\.\s+\*\*.+?\*\*/g).slice(1);
    const [evaluation, diagnosis, recommendations, disclaimer] = sections;

    // Deduplicate sources
    const uniqueSources = sources.filter(
        (source, index, self) =>
            index === self.findIndex((s) =>
                s.title === source.title && s.page === source.page
            )
    );

    return (
        <div className="bg-white rounded-lg shadow-md p-6 max-w-3xl mx-auto">
            {/* Header */}
            <div className="flex items-center mb-4">
                <div className="bg-blue-100 p-2 rounded-full mr-3">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <h2 className="text-xl font-semibold text-gray-800">Réponse du Psychiatre</h2>
            </div>

            {/* Structured Response */}
            <div className="space-y-4">
                {/* Evaluation */}
                <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-medium text-blue-800 mb-2">Évaluation</h3>
                    <div className="text-gray-700">
                        <ReactMarkdown>{evaluation}</ReactMarkdown>
                    </div>
                </div>

                {/* Diagnosis */}
                <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="font-medium text-purple-800 mb-2">Hypothèse Diagnostique</h3>
                    <div className="text-gray-700">
                        <ReactMarkdown>{diagnosis}</ReactMarkdown>
                    </div>
                </div>

                {/* Recommendations */}
                <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="font-medium text-green-800 mb-2">Recommandations</h3>
                    <div className="text-gray-700">
                        <ReactMarkdown>{recommendations}</ReactMarkdown>
                    </div>
                </div>

                {/* Disclaimer */}
                <div className="bg-yellow-50 p-3 rounded-lg border-l-4 border-yellow-400">
                    <div className="text-yellow-800 text-sm italic">
                        <ReactMarkdown>{disclaimer}</ReactMarkdown>
                    </div>
                </div>
            </div>

            {/* Deduplicated Sources */}
            <div className="mt-6">
                <h3 className="text-sm font-semibold text-gray-500 mb-2">Sources utilisées :</h3>
                <div
                    className="space-y-2 max-h-40 overflow-y-auto pr-2"
                    style={{ scrollbarWidth: 'thin', scrollbarColor: '#cbd5e1 #f1f5f9' }}
                >
                    {uniqueSources.map((source, index) => (
                        <div key={index} className="flex items-start text-sm text-gray-600">
                            <span className="mr-2">•</span>
                            <span>
                                {source.title} (Page {source.page})
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ChatResponse;