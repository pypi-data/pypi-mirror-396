class ComponentRepository:
    """
    Repository class for component-specific database operations
    """
    
    def __init__(self, db_connection):
        """
        Initialize repository with database connection
        """
        self.db = db_connection

    def save_component(self, technical_name, functional_name, id_type, folder, class_name, status):
        """
        Inserts a new component into schmesys.component table
        
        Args:
            technical_name (str): Technical name of the component
            id_type (int): Component type ID
            status (int): Component status
        """
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            
            insert_query = """
                INSERT INTO schmetrc.component(technical_name,functional_name, type_id, folder, class_name, status) 
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """

            cursor.execute(insert_query, (technical_name, functional_name, id_type, folder, class_name, status))
            component_id = cursor.fetchone()[0]
            self.db.commit_transaction()
            
            return component_id
            
        except Exception as e:
            self.db.rollback_transaction()
            raise Exception(f"Error saving component '{technical_name}': {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def query_components_by_type(self, id_type: int) -> list:
        """
        Consulta componentes de un tipo específico en la base de datos
        
        Args:
            id_type (int): ID del tipo de componente a consultar
        """
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            
            query = """
            SELECT * 
            FROM schmetrc.component 
            WHERE type_id = %s
            ORDER BY technical_name
            """
            
            cursor.execute(query, (id_type,))
            results = cursor.fetchall()
            
            components = []
            for row in results:
                component = {
                    'id': row[0],
                    'technical_name': row[1],
                    'id_type': row[2],
                    'status': row[3]
                }
                components.append(component)
            
            return components
            
        except Exception as e:
            raise Exception(f"Error querying components by type {id_type}: {str(e)}")
        finally:
            if cursor:
                cursor.close()

