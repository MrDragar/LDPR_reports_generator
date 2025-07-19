
import React, { useState } from 'react';
import { ChevronDownIcon } from './icons';

interface AccordionSectionProps {
  title: string;
  children: React.ReactNode;
  isOpenDefault?: boolean;
}

const AccordionSection: React.FC<AccordionSectionProps> = ({ title, children, isOpenDefault = false }) => {
  const [isOpen, setIsOpen] = useState(isOpenDefault);

  return (
    <div className="border border-gray-200 rounded-lg shadow-sm mb-4 bg-white">
      <button
        type="button"
        className="w-full flex justify-between items-center p-4 text-left text-lg font-semibold text-black"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{title}</span>
        <ChevronDownIcon className={`w-6 h-6 transform transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      <div
        className={`overflow-hidden transition-all duration-500 ease-in-out ${isOpen ? 'max-h-[5000px]' : 'max-h-0'}`}
      >
        <div className="p-4 border-t border-gray-200 text-black">
          {children}
        </div>
      </div>
    </div>
  );
};

export default AccordionSection;
