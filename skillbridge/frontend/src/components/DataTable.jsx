export default function DataTable({ columns, rows, keyField = "id" }) {
  if (!rows || rows.length === 0) {
    return <div className="text-sm text-slate-400 py-8 text-center">No data available.</div>;
  }
  return (
    <div className="overflow-x-auto border border-slate-200 rounded-xl bg-white">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-slate-50 border-b border-slate-200">
            {columns.map((col) => (
              <th key={col.key} className="text-left font-medium text-slate-500 px-4 py-2.5 whitespace-nowrap">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row[keyField]} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-2.5 text-slate-700 whitespace-nowrap">
                  {col.render ? col.render(row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
