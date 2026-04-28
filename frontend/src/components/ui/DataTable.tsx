import { useState } from "react";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { Input } from "./Input";
import { Button } from "./Button";
import { Skeleton } from "./Skeleton";

export interface ColumnDef<T> {
  key: string;
  header: string;
  filterMethod?: (item: T, query: string) => boolean;
  cell: (item: T) => React.ReactNode;
}

interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  isLoading?: boolean;
  searchable?: boolean;
  searchPlaceholder?: string;
  onRowClick?: (item: T) => void;
  rowsPerPage?: number;
}

export function DataTable<T>({
  data,
  columns,
  isLoading = false,
  searchable = false,
  searchPlaceholder = "Search...",
  onRowClick,
  rowsPerPage = 10
}: DataTableProps<T>) {
  const [query, setQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const filteredData = data.filter(item => {
    if (!query) return true;
    const filterableColumns = columns.filter(c => c.filterMethod);
    if (filterableColumns.length === 0) return true;
    return filterableColumns.some(c => c.filterMethod!(item, query));
  });

  const totalPages = Math.ceil(filteredData.length / rowsPerPage);
  const paginatedData = filteredData.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage);

  if (isLoading) {
    return (
      <div className="w-full space-y-4">
        {searchable && <Skeleton className="h-10 w-64" />}
        <div className="rounded-md border">
          <div className="h-12 border-b bg-muted/50" />
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex p-4 border-b last:border-0 gap-4">
              {columns.map((c, j) => (
                <Skeleton key={j} className="h-5 w-full flex-1" />
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      {searchable && (
        <div className="relative w-full max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder={searchPlaceholder}
            className="pl-9"
            value={query}
            onChange={(e) => { setQuery(e.target.value); setCurrentPage(1); }}
          />
        </div>
      )}

      <div className="rounded-md border overflow-hidden bg-card text-card-foreground">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/50 text-muted-foreground border-b border-border">
              <tr>
                {columns.map((col) => (
                  <th key={col.key} className="h-12 px-4 text-left align-middle font-medium">
                    {col.header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginatedData.length === 0 ? (
                <tr>
                  <td colSpan={columns.length} className="h-24 text-center text-muted-foreground">
                    No results.
                  </td>
                </tr>
              ) : (
                paginatedData.map((row, i) => (
                  <tr
                    key={i}
                    onClick={() => onRowClick && onRowClick(row)}
                    className={`border-b transition-colors ${
                      onRowClick ? "cursor-pointer hover:bg-muted/50" : ""
                    } last:border-0`}
                  >
                    {columns.map((col) => (
                      <td key={col.key} className="p-4 align-middle">
                        {col.cell(row)}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-end space-x-2">
          <div className="flex-1 text-sm text-muted-foreground">
            Showing {(currentPage - 1) * rowsPerPage + 1} to {Math.min(currentPage * rowsPerPage, filteredData.length)} of {filteredData.length} entries
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}
    </div>
  );
}
