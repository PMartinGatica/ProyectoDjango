import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import DailyControlsTable from '../components/DailyControlsTable';
import OrganizationChart from '../components/OrganizationChart';
import DocumentsPage from '../pages/Documentos'; // Cambiado para coincidir con "Documentos.jsx"
import LaunchesPage from '../pages/Lanzamientos'; // Cambiado para coincidir con "Lanzamientos.jsx"
import TrainingPage from '../pages/Formacion'; // Cambiado para coincidir con "Formacion.jsx"

const DashboardLayout = ({ user, onLogout }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activePage, setActivePage] = useState('inicio');
  const newsanRed = '#E30613'; // Color para KPIs

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleSetActivePage = (page) => {
    setActivePage(page);
    if (window.innerWidth < 768 && sidebarOpen) {
      setSidebarOpen(false);
    }
  };

  const renderPageContent = () => {
    const Card = ({ title, children, className = '' }) => (
      <div className={`bg-white p-4 rounded-lg shadow border border-gray-100 ${className}`}>
        {title && <h3 className="text-md font-semibold mb-3 text-gray-700">{title}</h3>}
        {children}
      </div>
    );

    const DefectTable = ({ data }) => (
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-left text-gray-500 uppercase">
              <th className="pb-1 pr-2 font-medium">Línea</th>
              <th className="pb-1 pr-2 font-medium">Top Defecto</th>
              <th className="pb-1 pr-2 font-medium">Causas (Resumen)</th>
              <th className="pb-1 pr-2 font-medium">Acciones (Resumen)</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={index} className="border-t border-gray-100">
                <td className="py-1.5 pr-2 font-medium text-gray-600">{item.linea}</td>
                <td className="py-1.5 pr-2 text-gray-600">{item.defecto}</td>
                <td className="py-1.5 pr-2 text-gray-600">{item.causas}</td>
                <td className="py-1.5 pr-2 text-gray-600">{item.acciones}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );

    const topDefectsData = [
      {
        linea: '06 Lamu',
        defecto: 'Rayón Tapa Trasera',
        causas: 'Manipulación indebida',
        acciones: 'Refuerzo capacitación',
      },
      {
        linea: '07 Lamu Lite',
        defecto: 'Falla Display (Línea)',
        causas: 'Proveedor / Presión',
        acciones: 'Ajuste proceso / Devolución',
      },
      {
        linea: '03 Lamu Lite GO',
        defecto: 'Tornillo Aislado',
        causas: 'Torqueadora / Posición',
        acciones: 'Calibración / Poka-yoke',
      },
    ];

    const getYesterdayDateFormatted = () => {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      return yesterday.toLocaleDateString('es-AR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      });
    };

    switch (activePage) {
      case 'inicio':
        const yesterdayDate = getYesterdayDateFormatted();
        return (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
              <Card title="FTY (First Time Yield)">
                <p className={`text-3xl font-bold text-[${newsanRed}]`}>98.5%</p>
              </Card>
              <Card title="DPHU (Defects Per Hundred Units)">
                <p className={`text-3xl font-bold text-[${newsanRed}]`}>1.5%</p>
              </Card>
              <Card title={`Top Defectos por Línea (${yesterdayDate})`}>
                <DefectTable data={topDefectsData} />
              </Card>
            </div>
            <DailyControlsTable />
            <OrganizationChart />
          </>
        );
      case 'documentos':
        return <DocumentsPage currentUser={user} />;
      case 'controles':
        return (
          <Card title="Registrar Control" className="p-6">
            Contenido de la página de Controles (Formularios, tablas, etc.)
          </Card>
        );
      case 'reportes':
        return (
          <Card title="Visualizar Reportes" className="p-6">
            Contenido de la página de Reportes (Gráficos, filtros, exportación)
          </Card>
        );
      case 'lanzamientos':
        return <LaunchesPage currentUser={user} />;
      case 'formacion':
        return <TrainingPage currentUser={user} />;
      default:
        return (
          <Card title="Página no encontrada" className="p-6">
            El contenido para '{activePage}' aún no está implementado.
          </Card>
        );
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black bg-opacity-50 md:hidden"
          onClick={toggleSidebar}
          aria-hidden="true"
        ></div>
      )}
      <Sidebar
        isOpen={sidebarOpen}
        toggleSidebar={toggleSidebar}
        activePage={activePage}
        setActivePage={handleSetActivePage}
        currentUser={user}
      />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header toggleSidebar={toggleSidebar} activePage={activePage} currentUser={user} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-4 md:p-6 lg:p-8">
          {renderPageContent()}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
