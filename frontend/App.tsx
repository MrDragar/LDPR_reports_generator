import React, { useState, useEffect } from 'react';
import { PlusIcon, TrashIcon, SpinnerIcon } from './components/icons';
import AccordionSection from './components/AccordionSection';

const SERVER_URL = process.env.SERVER_URL;

const INPUT_CLASS = "w-full p-2 border-2 border-[#005BBB] rounded-md focus:ring-2 focus:ring-[#FFD700] focus:border-[#FFD700] outline-none transition-shadow bg-gray-50 text-gray-900 placeholder:text-gray-500";
const TEXTAREA_CLASS = `${INPUT_CLASS} min-h-[100px]`;
const SELECT_CLASS = "w-full p-2 border-2 border-[#005BBB] rounded-md focus:ring-2 focus:ring-[#FFD700] focus:border-[#FFD700] outline-none transition-shadow bg-gray-50 text-gray-900";
const BUTTON_PRIMARY_CLASS = "bg-[#005BBB] text-white font-bold py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed";
const BUTTON_SECONDARY_CLASS = "bg-gray-200 text-gray-700 font-bold py-2 px-4 rounded-md hover:bg-gray-300 transition-colors flex items-center gap-2";
const BUTTON_IMPORT_CLASS = "bg-green-500 text-white font-bold py-2 px-4 rounded-md hover:bg-green-600 transition-colors";
const BUTTON_DANGER_CLASS = "bg-red-500 text-white font-bold py-2 px-4 rounded-md hover:bg-red-600 transition-colors";
const DYNAMIC_ITEM_CLASS = "p-4 border border-gray-200 rounded-lg mb-4 space-y-3 bg-white/50 overflow-y: auto";

const initialFormData = {
    general_info: {
        full_name: "",
        district: "",
        region: "",
        authority_name: "",
        term_start: "",
        term_end: "",
        links: [""],
        position: "",
        committees: [""],
        sessions_attended: {
            total: "",
            attended: "",
            committee_total: "",
            committee_attended: "",
            ldpr_total: "",
            ldpr_attended: "",
        },
    },
    legislation: [],
    citizen_requests: {
        total_requests: "",
        personal_meetings: "",
        requests: {
            utilities: "",
            pensions_and_social_payments: "",
            improvement: "",
            education: "",
            svo: "",
            road_maintenance: "",
            ecology: "",
            medicine_and_healthcare: "",
            public_transport: "",
            illegal_dumps: "",
            appeals_to_ldpr_chairman: "",
            legal_aid_requests: "",
            integrated_territory_development: "",
            stray_animal_issues: "",
            legislative_proposals: "",
        },
        responses: "",
        official_queries: "",
        examples: [""],
    },
    svo_support: {
        projects: [""],
    },
    project_activity: [],
    ldpr_orders: [],
    other_info: "",
};

const REQUEST_TOPICS_CONFIG = [
    { key: 'utilities', label: 'ЖКХ' },
    { key: 'pensions_and_social_payments', label: 'Пенсии и соцвыплаты' },
    { key: 'improvement', label: 'Благоустройство' },
    { key: 'education', label: 'Образование' },
    { key: 'svo', label: 'СВО' },
    { key: 'public_transport', label: 'Общественный транспорт' },
    { key: 'ecology', label: 'Экология' },
    { key: 'road_maintenance', label: 'Ремонт и содержание дорог' },
    { key: 'illegal_dumps', label: 'Несанкционированные свалки' },
    { key: 'appeals_to_ldpr_chairman', label: 'Обращения к Председателю ЛДПР' },
    { key: 'legal_aid_requests', label: 'Юридическая помощь' },
    { key: 'legislative_proposals', label: 'Законодательные инициативы' },
    { key: 'stray_animal_issues', label: 'Бездомные животные' },
    { key: 'integrated_territory_development', label: 'Развитие территорий' }
];

const Toast = ({ message, type, onDismiss }) => {
    useEffect(() => {
        const timer = setTimeout(onDismiss, 5000);
        return () => clearTimeout(timer);
    }, [onDismiss]);

    const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';

    return (
        <div className={`fixed top-5 right-5 ${bgColor} text-white py-3 px-5 rounded-lg shadow-xl z-50 flex items-center gap-2`}>
            {message}
            <button onClick={onDismiss} className="font-bold">X</button>
        </div>
    );
};

const Modal = ({ isOpen, onClose, onConfirm, title, message }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg max-w-md w-full">
                <h2 className="text-xl font-bold text-red-600 mb-4">{title}</h2>
                <p className="text-gray-700 mb-6">{message}</p>
                <div className="flex justify-end gap-4">
                    <button onClick={onClose} className={BUTTON_SECONDARY_CLASS}>
                        Отмена
                    </button>
                    <button onClick={onConfirm} className={BUTTON_DANGER_CLASS}>
                        Подтвердить
                    </button>
                </div>
            </div>
        </div>
    );
};

const App = () => {
    const [formData, setFormData] = useState(() => {
        try {
            const savedDraft = localStorage.getItem('ldpr-report-draft');
            if (savedDraft) {
                const parsedDraft = JSON.parse(savedDraft);
                if (!parsedDraft.citizen_requests.requests) {
                    parsedDraft.citizen_requests.requests = initialFormData.citizen_requests.requests;
                }
                return { ...initialFormData, ...parsedDraft };
            }
        } catch (error) {
            console.error("Failed to load draft from localStorage", error);
        }
        return initialFormData;
    });
    const [isLoading, setIsLoading] = useState(false);
    const [toast, setToast] = useState(null);
    const [validationErrors, setValidationErrors] = useState({});
    const [hasSubmitted, setHasSubmitted] = useState(false);
    const [showResetModal, setShowResetModal] = useState(false);

    useEffect(() => {
        const errors = {};

        // Required fields validation
        const requiredFields = [
            { path: 'general_info', key: 'full_name', label: 'ФИО депутата' },
            { path: 'general_info', key: 'district', label: 'Избирательный округ' },
            { path: 'general_info', key: 'region', label: 'Субъект Российской Федерации' },
            { path: 'general_info', key: 'authority_name', label: 'Наименование коллегиального органа власти' },
            { path: 'general_info', key: 'term_start', label: 'Начало полномочий' },
            { path: 'general_info', key: 'position', label: 'Должность' },
            { path: 'citizen_requests', key: 'personal_meetings', label: 'Количество личных приемов граждан' },
            { path: 'citizen_requests', key: 'responses', label: 'Количество данных ответов' },
            { path: 'citizen_requests', key: 'official_queries', label: 'Количество депутатских запросов' },
        ];

        requiredFields.forEach(({ path, key, label }) => {
            const value = formData[path][key];
            if (hasSubmitted && !value) {
                errors[`${path}.${key}`] = `${label}: обязательно для заполнения.`;
            }
        });

        // Numeric fields validation
        const numericFields = [
            { path: 'citizen_requests', key: 'personal_meetings', label: 'Количество личных приемов граждан и встреч с избирателями' },
            { path: 'citizen_requests', key: 'responses', label: 'Количество данных ответов на обращения граждан' },
            { path: 'citizen_requests', key: 'official_queries', label: 'Количество депутатских запросов и обращений' },
        ];

        numericFields.forEach(({ path, key, label }) => {
            const value = formData[path][key];
            if (value && !/^\d+$/.test(value)) {
                errors[`${path}.${key}`] = `${label}: должно быть целое число.`;
            }
        });

        // Request topics validation
        REQUEST_TOPICS_CONFIG.forEach(({ key, label }) => {
            const value = formData.citizen_requests.requests[key];
            if (hasSubmitted && !value) {
                errors[`requests.${key}`] = `${label}: обязательно для заполнения.`;
            }
            if (value && !/^\d+$/.test(value)) {
                errors[`requests.${key}`] = `${label}: должно быть целое число.`;
            }
        });

        // Sessions attended validation
        const sessionFields = [
            { total: 'total', attended: 'attended', label: 'Коллегиального органа власти' },
            { total: 'committee_total', attended: 'committee_attended', label: 'Комитетов/комиссий' },
            { total: 'ldpr_total', attended: 'ldpr_attended', label: 'Фракции ЛДПР' },
        ];

        sessionFields.forEach(({ total, attended, label }) => {
            const totalValue = formData.general_info.sessions_attended[total];
            const attendedValue = formData.general_info.sessions_attended[attended];

            if (hasSubmitted && !totalValue) {
                errors[`sessions_attended.${total}`] = `${label} (всего): обязательно для заполнения.`;
            }
            if (hasSubmitted && !attendedValue) {
                errors[`sessions_attended.${attended}`] = `${label} (посещено): обязательно для заполнения.`;
            }
            if (totalValue && !/^\d+$/.test(totalValue)) {
                errors[`sessions_attended.${total}`] = `${label} (всего): должно быть целое число.`;
            }
            if (attendedValue && !/^\d+$/.test(attendedValue)) {
                errors[`sessions_attended.${attended}`] = `${label} (посещено): должно быть целое число.`;
            }
            if (totalValue && attendedValue && parseInt(attendedValue) > parseInt(totalValue)) {
                errors[`sessions_attended.${attended}`] = `${label}: посещено не может превышать общее количество.`;
            }
        });

        // Legislation validation
        formData.legislation.forEach((item, index) => {
            if (hasSubmitted) {
                if (!item.title) {
                    errors[`legislation.${index}.title`] = `Инициатива #${index + 1}: Название законопроекта обязательно.`;
                }
                if (!item.summary) {
                    errors[`legislation.${index}.summary`] = `Инициатива #${index + 1}: Краткое описание обязательно.`;
                }
                if (!item.status) {
                    errors[`legislation.${index}.status`] = `Инициатива #${index + 1}: Статус обязателен.`;
                }
                if (item.status === 'Отклонен' && !item.rejection_reason) {
                    errors[`legislation.${index}.rejection_reason`] = `Инициатива #${index + 1}: Причина отказа обязательна.`;
                }
            }
        });

        // Project activity validation
        formData.project_activity.forEach((item, index) => {
            if (hasSubmitted) {
                if (!item.name) {
                    errors[`project_activity.${index}.name`] = `Проект #${index + 1}: Наименование обязательно.`;
                }
                if (!item.result) {
                    errors[`project_activity.${index}.result`] = `Проект #${index + 1}: Результаты обязательны.`;
                }
            }
        });

        // LDPR orders validation
        formData.ldpr_orders.forEach((item, index) => {
            if (hasSubmitted) {
                if (!item.instruction) {
                    errors[`ldpr_orders.${index}.instruction`] = `Поручение #${index + 1}: Конкретное поручение обязательно.`;
                }
                if (!item.action) {
                    errors[`ldpr_orders.${index}.action`] = `Поручение #${index + 1}: Проделанная работа обязательна.`;
                }
            }
        });

        setValidationErrors(errors);
    }, [formData, hasSubmitted]);

    useEffect(() => {
        try {
            const draft = JSON.stringify(formData);
            localStorage.setItem('ldpr-report-draft', draft);
        } catch (error) {
            console.error("Failed to save draft to localStorage", error);
        }
    }, [formData]);

    const cleanFormData = (data) => {
        const cleaned = { ...data };

        // Clean string arrays
        ['links', 'committees'].forEach(key => {
            cleaned.general_info[key] = cleaned.general_info[key].filter(item => item.trim() !== '');
        });
        cleaned.citizen_requests.examples = cleaned.citizen_requests.examples.filter(item => item.trim() !== '');
        cleaned.svo_support.projects = cleaned.svo_support.projects.filter(item => item.trim() !== '');

        // Clean legislation array
        cleaned.legislation = cleaned.legislation.filter(item => 
            item.title.trim() !== '' || 
            item.summary.trim() !== '' || 
            item.status.trim() !== '' ||
            item.rejection_reason.trim() !== ''
        );

        // Clean project activity and ldpr orders
        cleaned.project_activity = cleaned.project_activity.filter(item => 
            item.name.trim() !== '' || 
            item.result.trim() !== ''
        );
        cleaned.ldpr_orders = cleaned.ldpr_orders.filter(item => 
            item.instruction.trim() !== '' || 
            item.action.trim() !== ''
        );

        return cleaned;
    };

    const handleReset = () => {
        setFormData(initialFormData);
        localStorage.removeItem('ldpr-report-draft');
        setToast({ message: "Форма очищена", type: 'success' });
        setShowResetModal(false);
        setHasSubmitted(false);
    };

    const validateForm = () => {
        setHasSubmitted(true);
        const errors = {};

        // Required fields validation
        const requiredFields = [
            { path: 'general_info', key: 'full_name', label: 'ФИО депутата' },
            { path: 'general_info', key: 'district', label: 'Избирательный округ' },
            { path: 'general_info', key: 'region', label: 'Субъект Российской Федерации' },
            { path: 'general_info', key: 'authority_name', label: 'Наименование коллегиального органа власти' },
            { path: 'general_info', key: 'term_start', label: 'Начало полномочий' },
            { path: 'general_info', key: 'position', label: 'Должность' },
            { path: 'citizen_requests', key: 'personal_meetings', label: 'Количество личных приемов граждан' },
            { path: 'citizen_requests', key: 'responses', label: 'Количество данных ответов' },
            { path: 'citizen_requests', key: 'official_queries', label: 'Количество депутатских запросов' },
        ];

        requiredFields.forEach(({ path, key, label }) => {
            const value = formData[path][key];
            if (!value) {
                errors[`${path}.${key}`] = `${label}: обязательно для заполнения.`;
            }
        });

        // Validate request topics
        REQUEST_TOPICS_CONFIG.forEach(({ key, label }) => {
            if (!formData.citizen_requests.requests[key]) {
                errors[`requests.${key}`] = `${label}: обязательно для заполнения.`;
            }
        });

        // Validate sessions attended
        const sessionFields = [
            { total: 'total', attended: 'attended', label: 'Коллегиального органа власти' },
            { total: 'committee_total', attended: 'committee_attended', label: 'Комитетов/комиссий' },
            { total: 'ldpr_total', attended: 'ldpr_attended', label: 'Фракции ЛДПР' },
        ];

        sessionFields.forEach(({ total, attended, label }) => {
            if (!formData.general_info.sessions_attended[total]) {
                errors[`sessions_attended.${total}`] = `${label} (всего): обязательно для заполнения.`;
            }
            if (!formData.general_info.sessions_attended[attended]) {
                errors[`sessions_attended.${attended}`] = `${label} (посещено): обязательно для заполнения.`;
            }
        });

        setValidationErrors(prev => ({ ...prev, ...errors }));
        return Object.keys(errors).length === 0 && Object.keys(validationErrors).length === 0;
    };

    const downloadJson = (data) => {
        try {
            const jsonString = JSON.stringify(data, null, 2);
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');

            const fullName = data.general_info.full_name.trim() || 'deputy';
            const sanitizedName = fullName.toLowerCase().replace(/[\s/\\?%*:|"<>]/g, '_');
            const date = new Date().toISOString().split('T')[0];
            a.download = `ldpr_report_${sanitizedName}_${date}.json`;

            a.href = url;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (e) {
            console.error("Failed to create and download JSON file", e);
            throw new Error("Не удалось создать JSON файл для скачивания.");
        }
    };

    const handleImportJson = (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importedData = JSON.parse(e.target.result);
                if (!importedData.citizen_requests.requests) {
                    importedData.citizen_requests.requests = initialFormData.citizen_requests.requests;
                }
                setFormData({ ...initialFormData, ...importedData });
                setToast({ message: "Данные успешно импортированы", type: 'success' });
            } catch (error) {
                console.error("Failed to import JSON", error);
                setToast({ message: "Ошибка при импорте JSON файла", type: 'error' });
            }
        };
        reader.readAsText(file);
    };

    const handleExportJson = () => {
        try {
            const cleanedData = cleanFormData(formData);
            downloadJson(cleanedData);
            setToast({ message: "JSON файл успешно экспортирован", type: 'success' });
        } catch (error) {
            setToast({ message: "Ошибка при экспорте JSON файла", type: 'error' });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setHasSubmitted(true);
        if (!validateForm()) {
            setToast({ message: "Пожалуйста, исправьте ошибки в форме.", type: 'error' });
            return;
        }

        setIsLoading(true);
        setToast(null);

        try {
            const cleanedData = cleanFormData(formData);
            const response = await fetch(SERVER_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(cleanedData),
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const result = await response.json();
            if (result.status !== 'Succes' || !result.message) {
                throw new Error('Invalid server response');
            }

            const pdfUrl = result.message;
            const pdfResponse = await fetch(pdfUrl);
            if (!pdfResponse.ok) {
                throw new Error(`Failed to fetch PDF: ${pdfResponse.status}`);
            }

            const pdfBlob = await pdfResponse.blob();
            const url = URL.createObjectURL(pdfBlob);
            const a = document.createElement('a');
            const fullName = formData.general_info.full_name.trim() || 'deputy';
            const sanitizedName = fullName.toLowerCase().replace(/[\s/\\?%*:|"<>]/g, '_');
            const date = new Date().toISOString().split('T')[0];
            a.download = `ldpr_report_${sanitizedName}_${date}.pdf`;
            a.href = url;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            setToast({ message: "Отчёт успешно сформирован и скачан!", type: 'success' });
        } catch (error) {
            console.error("Submission failed:", error);
            const errorMessage = error instanceof Error ? error.message : "Ошибка при формировании отчёта.";
            setToast({ message: errorMessage, type: 'error' });
        } finally {
            setIsLoading(false);
        }
    };

    const handleNestedChange = (path, key, value) => {
        setFormData(prev => ({
            ...prev,
            [path]: {
                ...(prev[path]),
                [key]: value
            }
        }));
    };

    const handleDynamicListChange = (listName, index, field, value) => {
        setFormData(prev => {
            const list = [...(prev[listName])];
            list[index] = { ...list[index], [field]: value };
            return { ...prev, [listName]: list };
        });
    };

    const addDynamicListItem = (listName, newItem) => {
        setFormData(prev => ({
            ...prev,
            [listName]: [...(prev[listName]), newItem]
        }));
    };

    const removeDynamicListItem = (listName, index) => {
        setFormData(prev => ({
            ...prev,
            [listName]: (prev[listName]).filter((_, i) => i !== index)
        }))
    };

    const handleStringArrayChange = (path, subpath, index, value) => {
        setFormData(prev => {
            const section = { ...prev[path] };
            const list = [...(section[subpath])];
            list[index] = value;
            return { ...prev, [path]: { ...section, [subpath]: list }};
        });
    };

    const addStringArrayItem = (path, subpath) => {
        setFormData(prev => {
            const section = { ...prev[path] };
            const list = [...(section[subpath]), ""];
            return { ...prev, [path]: { ...section, [subpath]: list } };
        });
    };

    const removeStringArrayItem = (path, subpath, index) => {
        setFormData(prev => {
            const section = { ...prev[path] };
            const list = (section[subpath]).filter((_, i) => i !== index);
            return { ...prev, [path]: { ...section, [subpath]: list } };
        });
    };

    const renderError = (field) => validationErrors[field] && (
        <p className="text-red-500 text-sm mt-1">{validationErrors[field]}</p>
    );

    const totalRequests = REQUEST_TOPICS_CONFIG.reduce((sum, { key }) => {
        const value = formData.citizen_requests.requests[key] || '0';
        return sum + (parseInt(value) || 0);
    }, 0);

    return (
        <div className="bg-gray-100 min-h-screen p-4 sm:p-6 md:p-8">
            {toast && <Toast message={toast.message} type={toast.type} onDismiss={() => setToast(null)} />}
            <Modal
                isOpen={showResetModal}
                onClose={() => setShowResetModal(false)}
                onConfirm={handleReset}
                title="Внимание: Очистка формы"
                message="Вы уверены, что хотите очистить форму? Все введенные данные будут безвозвратно удалены. Это действие нельзя отменить."
            />
            <div className="max-w-4xl mx-auto">
                <header className="text-center mb-8">
                    <h1 className="text-3xl sm:text-4xl font-bold text-[#005BBB]">Отчёт депутата ЛДПР</h1>
                    <p className="text-black mt-2">О проделанной работе перед гражданами</p>
                    <p className="text-sm text-gray-600 mt-1">За первое полугодие 2025 года</p>
                    <p className="text-black mt-4">Заполните поля для автоматического создания отчёта о проделанной работе.</p>
                </header>

                <div className="flex flex-col sm:flex-row justify-center gap-4 mb-6">
                    <button
                        type="button"
                        onClick={() => setShowResetModal(true)}
                        className={`${BUTTON_DANGER_CLASS} w-full sm:w-auto`}
                    >
                        Очистить форму
                    </button>
                    <label className={`${BUTTON_IMPORT_CLASS} w-full sm:w-auto cursor-pointer flex items-center justify-center`}>
                        Загрузить черновик
                        <input
                            type="file"
                            accept=".json"
                            onChange={handleImportJson}
                            className="hidden"
                        />
                    </label>
                    <button
                        type="button"
                        onClick={handleExportJson}
                        className={`${BUTTON_SECONDARY_CLASS} w-full sm:w-auto cursor-pointer flex items-center justify-center`}
                    >
                        Выгрузить черновик
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <AccordionSection title="1. Общая информация" isOpenDefault={true}>
                        <div className="grid grid-cols-1 gap-4">
                            <div>
                                <label className="font-semibold block mb-1">ФИО депутата (сенатора)*</label>
                                <input
                                    type="text"
                                    value={formData.general_info.full_name}
                                    onChange={e => handleNestedChange('general_info', 'full_name', e.target.value)}
                                    className={`${INPUT_CLASS} ${validationErrors['general_info.full_name'] ? 'border-red-500' : ''}`}
                                    required
                                />
                                {renderError('general_info.full_name')}
                            </div>
                            <div>
                                <label className="font-semibold block mb-1">Избирательный округ*</label>
                                <input
                                    type="text"
                                    value={formData.general_info.district}
                                    onChange={e => handleNestedChange('general_info', 'district', e.target.value)}
                                    className={`${INPUT_CLASS} ${validationErrors['general_info.district'] ? 'border-red-500' : ''}`}
                                    placeholder="Территория, краткое описание"
                                    required
                                />
                                {renderError('general_info.district')}
                            </div>
                            <div>
                                <label className="font-semibold block mb-1">Субъект Российской Федерации*</label>
                                <input
                                    type="text"
                                    value={formData.general_info.region}
                                    onChange={e => handleNestedChange('general_info', 'region', e.target.value)}
                                    className={`${INPUT_CLASS} ${validationErrors['general_info.region'] ? 'border-red-500' : ''}`}
                                    required
                                />
                                {renderError('general_info.region')}
                            </div>
                            <div>
                                <label className="font-semibold block mb-1">Наименование коллегиального представительного органа власти*</label>
                                <input
                                    type="text"
                                    value={formData.general_info.authority_name}
                                    onChange={e => handleNestedChange('general_info', 'authority_name', e.target.value)}
                                    className={`${INPUT_CLASS} ${validationErrors['general_info.authority_name'] ? 'border-red-500' : ''}`}
                                    required
                                />
                                {renderError('general_info.authority_name')}
                            </div>
                            <div>
                                <label className="font-semibold block mb-1">Начало полномочий*</label>
                                <input
                                    type="text"
                                    placeholder="ДД.ММ.ГГГГ"
                                    value={formData.general_info.term_start}
                                    onChange={e => handleNestedChange('general_info', 'term_start', e.target.value)}
                                    className={`${INPUT_CLASS} ${validationErrors['general_info.term_start'] ? 'border-red-500' : ''}`}
                                    required
                                />
                                {renderError('general_info.term_start')}
                            </div>
                            <div>
                                <label className="font-semibold block mb-1">Окончание полномочий</label>
                                <input
                                    type="text"
                                    placeholder="ДД.ММ.ГГГГ"
                                    value={formData.general_info.term_end}
                                    onChange={e => handleNestedChange('general_info', 'term_end', e.target.value)}
                                    className={INPUT_CLASS}
                                />
                            </div>
                            <div>
                                <label className="font-semibold block mb-1">Должность (в коллегиальном органе власти)*</label>
                                <input
                                    type="text"
                                    value={formData.general_info.position}
                                    onChange={e => handleNestedChange('general_info', 'position', e.target.value)}
                                    className={`${INPUT_CLASS} ${validationErrors['general_info.position'] ? 'border-red-500' : ''}`}
                                    required
                                />
                                {renderError('general_info.position')}
                            </div>
                        </div>

                        <div className="mt-4">
                            <label className="font-semibold block mb-2">Ссылки (соцсети, сайт)</label>
                            {formData.general_info.links.map((link, index) => (
                                <div key={index} className="flex items-center gap-2 mb-2">
                                    <input
                                        type="url"
                                        value={link}
                                        onChange={e => handleStringArrayChange('general_info', 'links', index, e.target.value)}
                                        className={INPUT_CLASS}
                                        placeholder="https://..."
                                    />
                                    <button
                                        type="button"
                                        onClick={() => removeStringArrayItem('general_info', 'links', index)}
                                        className="p-2 text-red-500 hover:text-red-700"
                                    >
                                        <TrashIcon className="w-6 h-6"/>
                                    </button>
                                </div>
                            ))}
                            <button
                                type="button"
                                onClick={() => addStringArrayItem('general_info', 'links')}
                                className={`${BUTTON_SECONDARY_CLASS} text-sm`}
                            >
                                <PlusIcon className="w-4 h-4"/>Добавить ссылку
                            </button>
                        </div>

                        <div className="mt-4">
                            <label className="font-semibold block mb-2">В каких постоянных комитетах / комиссиях / рабочих группах состоит</label>
                            {formData.general_info.committees.map((committee, index) => (
                                <div key={index} className="flex items-center gap-2 mb-2">
                                    <input
                                        type="text"
                                        value={committee}
                                        onChange={e => handleStringArrayChange('general_info', 'committees', index, e.target.value)}
                                        className={INPUT_CLASS}
                                        placeholder="Комитет по..."
                                    />
                                    <button
                                        type="button"
                                        onClick={() => removeStringArrayItem('general_info', 'committees', index)}
                                        className="p-2 text-red-500 hover:text-red-700"
                                    >
                                        <TrashIcon className="w-6 h-6"/>
                                    </button>
                                </div>
                            ))}
                            <button
                                type="button"
                                onClick={() => addStringArrayItem('general_info', 'committees')}
                                className={`${BUTTON_SECONDARY_CLASS} text-sm`}
                            >
                                <PlusIcon className="w-4 h-4"/>Добавить комитет
                            </button>
                        </div>

                        <div className="mt-6 border-t pt-4">
                            <label className="font-semibold block mb-2">Статистика посещаемости заседаний (посещено / всего)*</label>
                            <div className="grid grid-cols-1 gap-4">
                                <div>
                                    <label className="text-sm block mb-1">Коллегиального органа власти</label>
                                    <div className="flex flex-col sm:flex-row gap-2">
                                        <div className="w-full">
                                            <input
                                                type="text"
                                                placeholder="Посещено"
                                                value={formData.general_info.sessions_attended.attended}
                                                onChange={e => handleNestedChange('general_info', 'sessions_attended', {
                                                    ...formData.general_info.sessions_attended,
                                                    attended: e.target.value
                                                })}
                                                className={`${INPUT_CLASS} ${validationErrors['sessions_attended.attended'] ? 'border-red-500' : ''}`}
                                                required
                                            />
                                            {renderError('sessions_attended.attended')}
                                        </div>
                                        <div className="w-full">
                                            <input
                                                type="text"
                                                placeholder="Всего"
                                                value={formData.general_info.sessions_attended.total}
                                                onChange={e => handleNestedChange('general_info', 'sessions_attended', {
                                                    ...formData.general_info.sessions_attended,
                                                    total: e.target.value
                                                })}
                                                className={`${INPUT_CLASS} ${validationErrors['sessions_attended.total'] ? 'border-red-500' : ''}`}
                                                required
                                            />
                                            {renderError('sessions_attended.total')}
                                        </div>
                                    </div>
                                </div>
                                <div>
                                    <label className="text-sm block mb-1">Комитетов / комиссий</label>
                                    <div className="flex flex-col sm:flex-row gap-2">
                                        <div className="w-full">
                                            <input
                                                type="text"
                                                placeholder="Посещено"
                                                value={formData.general_info.sessions_attended.committee_attended}
                                                onChange={e => handleNestedChange('general_info', 'sessions_attended', {
                                                    ...formData.general_info.sessions_attended,
                                                    committee_attended: e.target.value
                                                })}
                                                className={`${INPUT_CLASS} ${validationErrors['sessions_attended.committee_attended'] ? 'border-red-500' : ''}`}
                                                required
                                            />
                                            {renderError('sessions_attended.committee_attended')}
                                        </div>
                                        <div className="w-full">
                                            <input
                                                type="text"
                                                placeholder="Всего"
                                                value={formData.general_info.sessions_attended.committee_total}
                                                onChange={e => handleNestedChange('general_info', 'sessions_attended', {
                                                    ...formData.general_info.sessions_attended,
                                                    committee_total: e.target.value
                                                })}
                                                className={`${INPUT_CLASS} ${validationErrors['sessions_attended.committee_total'] ? 'border-red-500' : ''}`}
                                                required
                                            />
                                            {renderError('sessions_attended.committee_total')}
                                        </div>
                                    </div>
                                </div>
                                <div>
                                    <label className="text-sm block mb-1">Фракции ЛДПР</label>
                                    <div className="flex flex-col sm:flex-row gap-2">
                                        <div className="w-full">
                                            <input
                                                type="text"
                                                placeholder="Посещено"
                                                value={formData.general_info.sessions_attended.ldpr_attended}
                                                onChange={e => handleNestedChange('general_info', 'sessions_attended', {
                                                    ...formData.general_info.sessions_attended,
                                                    ldpr_attended: e.target.value
                                                })}
                                                className={`${INPUT_CLASS} ${validationErrors['sessions_attended.ldpr_attended'] ? 'border-red-500' : ''}`}
                                                required
                                            />
                                            {renderError('sessions_attended.ldpr_attended')}
                                        </div>
                                        <div className="w-full">
                                            <input
                                                type="text"
                                                placeholder="Всего"
                                                value={formData.general_info.sessions_attended.ldpr_total}
                                                onChange={e => handleNestedChange('general_info', 'sessions_attended', {
                                                    ...formData.general_info.sessions_attended,
                                                    ldpr_total: e.target.value
                                                })}
                                                className={`${INPUT_CLASS} ${validationErrors['sessions_attended.ldpr_total'] ? 'border-red-500' : ''}`}
                                                required
                                            />
                                            {renderError('sessions_attended.ldpr_total')}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </AccordionSection>

                    <AccordionSection title="2. Законотворческая (нормотворческая) деятельность">
                        <p className="text-black text-sm mb-4">Включите сюда инициативы, разработанные самостоятельно или в соавторстве с иными депутатами (сенаторами).</p>
                        
                        <div className="max-h-[620px] overflow-y-auto pr-2"> 
                            {formData.legislation.map((item, index) => (
                                <div key={index} className={DYNAMIC_ITEM_CLASS}>
                                    <div className="flex justify-between items-start">
                                        <h3 className="font-semibold text-lg text-black">Инициатива #{index + 1}</h3>
                                        <button
                                            type="button"
                                            onClick={() => removeDynamicListItem('legislation', index)}
                                            className="p-1 text-red-500 hover:text-red-700"
                                        >
                                            <TrashIcon className="w-6 h-6"/>
                                        </button>
                                    </div>
                                    <div>
                                        <label className="font-semibold block mb-1">Название законопроекта*</label>
                                        <input
                                            type="text"
                                            value={item.title}
                                            onChange={e => handleDynamicListChange('legislation', index, 'title', e.target.value)}
                                            className={`${INPUT_CLASS} ${validationErrors[`legislation.${index}.title`] ? 'border-red-500' : ''}`}
                                            required
                                        />
                                        {renderError(`legislation.${index}.title`)}
                                    </div>
                                    <div>
                                        <label className="font-semibold block mb-1">Краткое описание содержания законопроекта*</label>
                                        <textarea
                                            value={item.summary}
                                            onChange={e => handleDynamicListChange('legislation', index, 'summary', e.target.value)}
                                            className={`${TEXTAREA_CLASS} ${validationErrors[`legislation.${index}.summary`] ? 'border-red-500' : ''}`}
                                            required
                                        ></textarea>
                                        {renderError(`legislation.${index}.summary`)}
                                    </div>
                                    <div>
                                        <label className="font-semibold block mb-1 text-sm">Результат рассмотрения*</label>
                                        <select
                                            value={item.status}
                                            onChange={e => handleDynamicListChange('legislation', index, 'status', e.target.value)}
                                            className={`${SELECT_CLASS} ${validationErrors[`legislation.${index}.status`] ? 'border-red-500' : ''}`}
                                            required
                                        >
                                            <option value="">Выберите статус</option>
                                            <option value="Внесен и находится на рассмотрении">Внесен и находится на рассмотрении</option>
                                            <option value="Принят">Принят</option>
                                            <option value="Отклонен">Отклонен</option>
                                        </select>
                                        {renderError(`legislation.${index}.status`)}
                                    </div>
                                    {item.status === 'Отклонен' && (
                                        <div>
                                            <label className="font-semibold block mb-1 text-sm">Причина отказа с указанием субъекта отклонения*</label>
                                            <textarea
                                                value={item.rejection_reason}
                                                onChange={e => handleDynamicListChange('legislation', index, 'rejection_reason', e.target.value)}
                                                className={`${TEXTAREA_CLASS} min-h-[44px] ${validationErrors[`legislation.${index}.rejection_reason`] ? 'border-red-500' : ''}`}
                                                required
                                            ></textarea>
                                            {renderError(`legislation.${index}.rejection_reason`)}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                        
                        <button
                            type="button"
                            onClick={() => addDynamicListItem('legislation', { title: '', summary: '', status: '', rejection_reason: '' })}
                            className={`${BUTTON_SECONDARY_CLASS} mt-4`}
                        >
                            <PlusIcon className="w-5 h-5"/>Добавить инициативу
                        </button>
                    </AccordionSection>

                    <AccordionSection title="3. Работа с обращениями граждан">
                        <div className="grid grid-cols-1 gap-4 mb-4">
                            <div>
                                <label className="font-semibold block mb-1">Количество личных приемов граждан и встреч с избирателями*</label>
                                <input
                                    type="text"
                                    value={formData.citizen_requests.personal_meetings}
                                    onChange={e => handleNestedChange('citizen_requests', 'personal_meetings', e.target.value)}
                                    className={`${INPUT_CLASS} ${validationErrors['citizen_requests.personal_meetings'] ? 'border-red-500' : ''}`}
                                    required
                                />
                                {renderError('citizen_requests.personal_meetings')}
                            </div>
                            <div>
                                <label className="font-semibold block mb-1">Количество данных ответов на обращения граждан*</label>
                                <input
                                    type="text"
                                    value={formData.citizen_requests.responses}
                                    onChange={e => handleNestedChange('citizen_requests', 'responses', e.target.value)}
                                    className={`${INPUT_CLASS} ${validationErrors['citizen_requests.responses'] ? 'border-red-500' : ''}`}
                                    required
                                />
                                {renderError('citizen_requests.responses')}
                            </div>
                            <div>
                                <label className="font-semibold block mb-1">Количество депутатских запросов и обращений в органы власти и иные организации по поступившим обращениям граждан*</label>
                                <input
                                    type="text"
                                    value={formData.citizen_requests.official_queries}
                                    onChange={e => handleNestedChange('citizen_requests', 'official_queries', e.target.value)}
                                    className={`${INPUT_CLASS} ${validationErrors['citizen_requests.official_queries'] ? 'border-red-500' : ''}`}
                                    required
                                />
                                {renderError('citizen_requests.official_queries')}
                            </div>
                        </div>

                        <div className="border-t pt-4">
                            <label className="font-semibold block mb-2">Общее количество поступивших обращений за отчетный период*</label>
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                                {REQUEST_TOPICS_CONFIG.map(topic => (
                                    <div key={topic.key}>
                                        <label className="text-sm block mb-1">{topic.label}</label>
                                        <input
                                            type="text"
                                            value={formData.citizen_requests.requests[topic.key] || ''}
                                            onChange={e => handleNestedChange('citizen_requests', 'requests', {
                                                ...formData.citizen_requests.requests,
                                                [topic.key]: e.target.value
                                            })}
                                            className={`${INPUT_CLASS} ${validationErrors[`requests.${topic.key}`] ? 'border-red-500' : ''}`}
                                            required
                                        />
                                        {renderError(`requests.${topic.key}`)}
                                    </div>
                                ))}
                            </div>
                            <div className="mt-4">
                                <p className="font-semibold">Общее количество принятых обращений за отчетный период: <span className="font-bold text-[#005BBB]">{totalRequests}</span></p>
                            </div>
                        </div>

                        <div className="mt-6 border-t pt-4">
                            <label className="font-semibold block mb-2">Несколько примеров с результатами работы по отдельным обращениям граждан (без публикации персональных данных заявителей)</label>
                            <p className="text-black text-sm mb-3">Укажите в свободной форме</p>
                            {formData.citizen_requests.examples.map((example, index) => (
                                <div key={index} className="flex items-center gap-2 mb-2">
                                    <input
                                        type="text"
                                        value={example}
                                        onChange={e => handleStringArrayChange('citizen_requests', 'examples', index, e.target.value)}
                                        className={INPUT_CLASS}
                                        placeholder="Укажите в свободной форме..."
                                    />
                                    <button
                                        type="button"
                                        onClick={() => removeStringArrayItem('citizen_requests', 'examples', index)}
                                        className="p-2 text-red-500 hover:text-red-700"
                                    >
                                        <TrashIcon className="w-6 h-6"/>
                                    </button>
                                </div>
                            ))}
                            <button
                                type="button"
                                onClick={() => addStringArrayItem('citizen_requests', 'examples')}
                                className={`${BUTTON_SECONDARY_CLASS} text-sm`}
                            >
                                <PlusIcon className="w-4 h-4"/>Добавить пример
                            </button>
                        </div>
                    </AccordionSection>

                    <AccordionSection title="4. Работа с участниками СВО и членами их семей">
                        <p className="text-black text-sm mb-4">Укажите в свободной форме информацию о деятельности с участниками СВО и их семьями, волонтерскими и иными организациями, а также о реализованных проектах и мероприятиях по этой тематике.</p>
                        <label className="font-semibold block mb-2">Проекты и мероприятия</label>
                        {formData.svo_support.projects.map((project, index) => (
                            <div key={index} className="flex items-center gap-2 mb-2">
                                <input
                                    type="text"
                                    value={project}
                                    onChange={e => handleStringArrayChange('svo_support', 'projects', index, e.target.value)}
                                    className={INPUT_CLASS}
                                    placeholder="Укажите в свободной форме..."
                                />
                                <button
                                    type="button"
                                    onClick={() => removeStringArrayItem('svo_support', 'projects', index)}
                                    className="p-2 text-red-500 hover:text-red-700"
                                    >
                                    <TrashIcon className="w-6 h-6"/>
                                </button>
                            </div>
                        ))}
                        <button
                            type="button"
                            onClick={() => addStringArrayItem('svo_support', 'projects')}
                            className={`${BUTTON_SECONDARY_CLASS} text-sm`}
                        >
                            <PlusIcon className="w-4 h-4"/>Добавить проект
                        </button>
                    </AccordionSection>

                    <AccordionSection title="5. Представительская и проектная деятельность">
                        <p className="text-black text-sm mb-4">Укажите в свободной форме информацию о наиболее значимых проектах и мероприятиях, которые вы реализовали самостоятельно или в которых принимали участие.</p>
                        
                        {/* Контейнер с скроллом */}
                        <div className="max-h-[620px] overflow-y-auto pr-2 mb-4">
                            {formData.project_activity.map((item, index) => (
                                <div key={index} className={DYNAMIC_ITEM_CLASS}>
                                    <div className="flex justify-between items-start">
                                        <h3 className="font-semibold text-lg text-black">Проект/мероприятие #{index + 1}</h3>
                                        <button
                                            type="button"
                                            onClick={() => removeDynamicListItem('project_activity', index)}
                                            className="p-1 text-red-500 hover:text-red-700"
                                        >
                                            <TrashIcon className="w-6 h-6"/>
                                        </button>
                                    </div>
                                    <div>
                                        <label className="font-semibold block mb-1">Наименование*</label>
                                        <input
                                            type="text"
                                            value={item.name}
                                            onChange={e => handleDynamicListChange('project_activity', index, 'name', e.target.value)}
                                            className={`${INPUT_CLASS} ${validationErrors[`project_activity.${index}.name`] ? 'border-red-500' : ''}`}
                                            required
                                        />
                                        {renderError(`project_activity.${index}.name`)}
                                    </div>
                                    <div className="mt-3">
                                        <label className="font-semibold block mb-1">Результаты реализации (участия)*</label>
                                        <textarea
                                            value={item.result}
                                            onChange={e => handleDynamicListChange('project_activity', index, 'result', e.target.value)}
                                            className={`${TEXTAREA_CLASS} ${validationErrors[`project_activity.${index}.result`] ? 'border-red-500' : ''}`}
                                            required
                                        ></textarea>
                                        {renderError(`project_activity.${index}.result`)}
                                    </div>
                                </div>
                            ))}
                        </div>
                        
                        <button
                            type="button"
                            onClick={() => addDynamicListItem('project_activity', { name: '', result: '' })}
                            className={`${BUTTON_SECONDARY_CLASS}`}
                        >
                            <PlusIcon className="w-5 h-5"/>Добавить проект
                        </button>
                    </AccordionSection>

                    <AccordionSection title="6. Работа по реализации поручений Председателя ЛДПР">
                        <p className="text-black text-sm mb-4">Укажите конкретные поручения Председателя ЛДПР и информацию о проделанной работе по их реализации (мероприятия, законопроекты, контрольные мероприятия и т.п.).</p>
                        
                        {/* Контейнер с скроллом */}
                        <div className="max-h-[620px] overflow-y-auto pr-2 mb-4">
                            {formData.ldpr_orders.map((item, index) => (
                                <div key={index} className={DYNAMIC_ITEM_CLASS}>
                                    <div className="flex justify-between items-start">
                                        <h3 className="font-semibold text-lg text-black">Поручение #{index + 1}</h3>
                                        <button
                                            type="button"
                                            onClick={() => removeDynamicListItem('ldpr_orders', index)}
                                            className="p-1 text-red-500 hover:text-red-700"
                                        >
                                            <TrashIcon className="w-6 h-6"/>
                                        </button>
                                    </div>
                                    <div>
                                        <label className="font-semibold block mb-1">Конкретное поручение*</label>
                                        <textarea
                                            value={item.instruction}
                                            onChange={e => handleDynamicListChange('ldpr_orders', index, 'instruction', e.target.value)}
                                            className={`${TEXTAREA_CLASS} ${validationErrors[`ldpr_orders.${index}.instruction`] ? 'border-red-500' : ''}`}
                                            required
                                        ></textarea>
                                        {renderError(`ldpr_orders.${index}.instruction`)}
                                    </div>
                                    <div className="mt-3">
                                        <label className="font-semibold block mb-1">Проделанная работа по реализации*</label>
                                        <textarea
                                            value={item.action}
                                            onChange={e => handleDynamicListChange('ldpr_orders', index, 'action', e.target.value)}
                                            className={`${TEXTAREA_CLASS} ${validationErrors[`ldpr_orders.${index}.action`] ? 'border-red-500' : ''}`}
                                            required
                                        ></textarea>
                                        {renderError(`ldpr_orders.${index}.action`)}
                                    </div>
                                </div>
                            ))}
                        </div>
                        
                        <button
                            type="button"
                            onClick={() => addDynamicListItem('ldpr_orders', { instruction: '', action: '' })}
                            className={`${BUTTON_SECONDARY_CLASS}`}
                        >
                            <PlusIcon className="w-5 h-5"/>Добавить поручение
                        </button>
                    </AccordionSection>

                    <AccordionSection title="7. Иная значимая информация">
                        <label className="font-semibold block mb-1">Опишите другую важную деятельность, не вошедшую в предыдущие разделы</label>
                        <textarea
                            value={formData.other_info}
                            onChange={e => setFormData({ ...formData, other_info: e.target.value })}
                            className={TEXTAREA_CLASS}
                        ></textarea>
                    </AccordionSection>

                    <div className="flex justify-center pt-6 border-t border-gray-300">
                        <button
                            type="submit"
                            className={`${BUTTON_PRIMARY_CLASS} w-full sm:w-auto flex items-center justify-center gap-2`}
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <SpinnerIcon className="w-5 h-5" />
                                    <span>Формирование...</span>
                                </>
                            ) : (
                                "Сформировать отчёт"
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default App;
