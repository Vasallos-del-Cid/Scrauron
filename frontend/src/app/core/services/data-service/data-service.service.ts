import { BehaviorSubject, Observable, throwError } from 'rxjs';
import {
  HttpClient,
  HttpErrorResponse,
  HttpHeaders,
} from '@angular/common/http';

import { catchError, finalize, tap } from 'rxjs/operators';
import { Identificable } from './identificable.model';
import { ApiOptions } from './api-options.interface';

/**
 * Servicio base que encapsula lógica CRUD genérica con almacenamiento en memoria
 * y gestión centralizada de errores, callbacks y resultados.
 *
 * @typeParam T - Tipo de entidad que debe extender de Identificable (_id obligatorio).
 */
export abstract class DataService<T extends Identificable> {
  /** Fuente de datos reactiva
   * @protected
   * @type {BehaviorSubject<T[]>}
   * @description Almacena la lista de items y permite su suscripción.
   * @see {@link items$} para acceder a la lista de items como Observable.
   */
  protected readonly _items$ = new BehaviorSubject<T[]>([]);

  /** Observable que expone la lista de items reactiva
   *
   * Subscribe a este observable para recibir actualizaciones en tiempo real incluyendo en el html:
   *
   * ```html
   * <!-- En el syncfusion  -->
   * <ejs-grid #grid [dataSource]="items$ | async" [...]>
   * ````
   *
   * Requiere declarar en el component.ts   items$: Observable<T[]>
   * o usar {@link CrudAbstractMethodsComponent} que ya lo tiene declarado.
   *
   * @public
   * @type {Observable<T[]>}
   * @description Permite a los componentes suscribirse a los cambios en la lista de items.
   *
   * @see {@link _items$} para acceder a la fuente de datos reactiva.
   * @see {@link BehaviorSubject} para más información sobre su uso.
   * @see {@link Observable} para más información sobre la suscripción a cambios.
   */
  public readonly items$ = this._items$.asObservable();

  /** Opciones HTTP por defecto (JSON) */
  private readonly httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
  };

  private readonly url: string;

  /**
   * @param http HttpClient de Angular
   * @param endpoint nombre del endpoint (ej: 'fuentes')
   * @param baseUrl URL base de la API (default: 'http://localhost:5000/api')
   */
  constructor(
    protected http: HttpClient,
    protected endpoint: string,
    protected baseUrl: string = 'http://localhost:5000/api'
  ) {
    this.url = `${this.baseUrl}/${this.endpoint}`;
  }

  /**
   * Recupera todos los elementos desde la API y actualiza el observable local.
   *
   * por defecto , se devuelve el listado completo de elementos, si no es vacio y NO se muestra mensaje de éxito.
   *
   * @param options Opciones de éxito, error y callback
   *
   * {@link ApiOptions} para más información sobre las opciones
   */
  getAll(options?: ApiOptions<T[]>): void {
    this.http
      .get<T[]>(this.url, this.httpOptions)
      .pipe(
        this.wrapHandlers(
          (data) => {
            this._items$.next(data);
            options?.success?.(data);
          },
          options,
          undefined
        ) // false para no mostrar mensaje de éxito
      )
      .subscribe();
  }

  /**
   * Recupera un elemento por su ID desde la API.
   * No modifica el listado local.
   *
   * @param id ID del elemento a recuperar
   * @param options Opciones de éxito, error y callback
   *
   * {@link ApiOptions} para más información sobre las opciones
   */
  getOne(id: string, options?: ApiOptions<T>): void {
    this.http
      .get<T>(`${this.url}/${id}`, this.httpOptions)
      .pipe(
        this.wrapHandlers(
          (item) => options?.success?.(item),
          options,
          undefined // no mostramos mensaje por defecto en lectura
        )
      )
      .subscribe();
  }

  /**
   * Crea un nuevo elemento en la API y lo añade a la lista local.
   * @param item Objeto a crear
   * @param options Opciones de éxito, error y callback
   *
   * {@link ApiOptions} para más información sobre las opciones
   */
  create(item: T, options?: ApiOptions<T>): void {
    this.http
      .post<T>(this.url, item, this.httpOptions)
      .pipe(
        this.wrapHandlers(
          (created) => {
            const nuevos = [...this._items$.getValue(), created];
            this._items$.next(nuevos);
            options?.success?.(created);
          },
          options,
          '🖫 Elemento creado correctamente'
        ) // true para mostrar mensaje de éxito
      )
      .subscribe();
  }

  /**
   * Actualiza parcialmente un elemento usando su ID.
   * @param id ID del elemento a actualizar
   * @param cambios Objeto parcial con los campos a modificar
   * @param options Opciones de éxito, error y callback
   *
   * {@link ApiOptions} para más información sobre las opciones
   */
  update(id: string, cambios: Partial<T>, options?: ApiOptions<T>): void {
    this.http
      .patch<T>(`${this.url}/${id}`, cambios, this.httpOptions)
      .pipe(
        this.wrapHandlers(
          (updated) => {
            const actualizados = this._items$
              .getValue()
              .map((i) => (i._id === id ? updated : i));
            this._items$.next(actualizados);
            options?.success?.(updated);
          },
          options,
          '🖫 Elemento actualizado correctamente'
        ) // true para mostrar mensaje de éxito
      )
      .subscribe();
  }

  /**
   * Elimina un elemento por su ID y actualiza el listado local.
   * @param id ID del elemento a eliminar
   * @param options Opciones de éxito, error y callback
   *
   * {@link ApiOptions} para más información sobre las opciones
   */
  delete(id: string, options?: ApiOptions<void>): void {
    this.http
      .delete<void>(`${this.url}/${id}`, this.httpOptions)
      .pipe(
        this.wrapHandlers(
          () => {
            const nuevos = this._items$.getValue().filter((i) => i._id !== id);
            this._items$.next(nuevos);
            options?.success?.();
          },
          options,
          '🗑 Elemento eliminado correctamente'
        ) // true para mostrar mensaje de éxito
      )
      .subscribe();
  }

  /**
   * Decide si hacer `create` o `update` automáticamente según si el objeto tiene `_id`.
   * @param item Objeto a guardar
   * @param edicion `true` si se trata de una edición
   * @param options Opciones de éxito, error y callback
   *
   * {@link ApiOptions} para más información sobre las opciones
   */
  guardar(item: T, edicion: boolean, options?: ApiOptions<T>): void {
    if (edicion && item._id) {
      this.update(item._id, item, options);
    } else {
      this.create(item, options);
    }
  }

  /**
   * Centraliza el manejo de errores, éxito y callbacks para cualquier operación HTTP.
   *
   * lanza las {@link ApiOptions} success y failure y callback si se han definido.
   * si no se han definido, lanza mensaje genérico.
   *
   * @param onSuccess Función a ejecutar si la respuesta es correcta
   * @param options ApiOptions para manejar errores y callbacks
   * @param mensajeExito (opcional) Mensaje de éxito a mostrar
   *
   * {@link ApiOptions} para más información sobre las opciones
   * @returns Un operador que se puede usar en `.pipe()`
   */
  private wrapHandlers<T>(
    onSuccess: (data: T) => void,
    options?: ApiOptions<T>,
    mensajeExito?: string // para decidir si se muestra mensaje
  ) {
    return (source: Observable<T>) =>
      source.pipe(
        tap((data) => {
          try {
            onSuccess(data);
            if (!options?.success && !options?.silent && mensajeExito) {
              alert(mensajeExito);
            }
            options?.success?.(data);
          } catch (e) {
            console.error('Error ejecutando success():', e);
          }
        }),
        catchError((error: HttpErrorResponse) => {
          if (!options?.silent) {
            let msg = 'Error en la operación';
            if (error.status === 0) {
              msg = 'Error de conexión. Verifica el servidor.';
            } else if (error.status === 401) {
              msg = 'No tienes permiso para realizar esta operación.';
            } else if (error.status === 404) {
              msg = 'Elemento no encontrado.';
            } else if (error.status === 500) {
              msg = 'Error interno del servidor.';
            } else if (error.status === 400) {
              msg = 'Error de validación. Revisa los datos enviados.';
            } else if (error.status === 403) {
              msg =
                'Acceso denegado. No tienes permiso para realizar esta operación.';
            }
            msg = msg + '\n' + `Codigo: ${error.status}\n` +  error.error.error || error.message || error.statusText ||  'Error desconocido';
            console.error('===Error===:', error);

            alert(`❌ ${msg}`);
          }
          options?.failure?.(error);
          return throwError(() => error);
        }),
        finalize(() => options?.callback?.())
      );
  }
}
