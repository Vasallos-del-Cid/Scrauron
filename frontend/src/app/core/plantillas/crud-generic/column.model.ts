import { TemplateRef } from "@angular/core";

// column.model.ts
export interface ColumnConfig {
  field: string;
  headerText: string;
  width?: number;
  textAlign?: 'Left'|'Center'|'Right';
  type?: 'string'|'number'|'datetime'|'boolean';
  format?: string;
  isPrimaryKey?: boolean;
  
}