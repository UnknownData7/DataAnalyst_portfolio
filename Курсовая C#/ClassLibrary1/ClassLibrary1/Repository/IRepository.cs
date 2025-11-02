using ClassLibrary1.Models;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ClassLibrary1.Repository
{
    public interface IRepository
    {
        #region Методы  возвращают коллекцию объектов
        //ObservableCollection - коллекция с уведомленим об изменении
        ObservableCollection<Product> GetProducts(int sort = 0);
        ObservableCollection<Client> GetClients(int sort = 0);
        ObservableCollection<Order> GetOrders(int sort = 0);
        #endregion

        #region Добавление элементов в коллекцию
        bool AddProduct(Product product);
        bool AddClient(Client client);
        bool AddOrder(Order order);
        #endregion
    }
}
