// utils/parseResponse.ts
import ReactMarkdown from 'react-markdown';

export const parseResponse = (rawResponse: string) => {
  const sections = rawResponse.split(/\d+\.\s+\*\*.+?\*\*/g).slice(1);
  
  return {
    evaluation: sections[0] || '',
    diagnosis: sections[1] || '',
    recommendations: sections[2] || '',
    disclaimer: sections[3] || ''
  };
};