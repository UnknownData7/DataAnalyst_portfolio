using ClassLibrary1.Models;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ClassLibrary1.Repository
{
    public class SimpleRepository : IRepository
    {
        //Коллекции имитируют БД
        ObservableCollection<Product> products = new ObservableCollection<Product>()
        {
            new Product()
            {
                Id = 1, Name = "Pen", Price = 25.12m, Quantity = 50,
                Description = "Good pencil"
            },
            new Product()
            {
                Id = 2, Name = "Table", Price = 125.12m, Quantity = 10,
                Description = "A dinner table"
            },
            new Product()
            {
                Id = 3, Name = "Bear", Price = 150.12m, Quantity = 30,
                Description = "Toys"
            }
        };

        public bool AddClient(Client client)
        {
            throw new NotImplementedException();
        }

        public bool AddOrder(Order order)
        {
            throw new NotImplementedException();
        }

        public bool AddProduct(Product product)
        {
            throw new NotImplementedException();
        }

        public ObservableCollection<Client> GetClients(int sort = 0)
        {
            throw new NotImplementedException();
        }

        public ObservableCollection<Order> GetOrders(int sort = 0)
        {
            throw new NotImplementedException();
        }

        public ObservableCollection<Product> GetProducts(int sort = 0)
        {
            throw new NotImplementedException();
        }
        ObservableCollection<Client> clients = new ObservableCollection<Client>()
        {
            new Client()
            {
                Id = 1, Name = "Ivanov", FirstName = "Ivan", MiddleName = "Ivanovich",
                Description = "Vip"
            },
            new Client()
            {
                Id = 2, Name = "Petrov", FirstName = "Peter", MiddleName = "Petrovich",
                Description = "Loser"
            },
            new Client()
            {
                Id =3, Name = "Sidorov", FirstName = "Sidor",
                MiddleName = "Sidorovich", Description = "Big Boss"
            }
        };
        ObservableCollection<Order> orders = new ObservableCollection<Order>();
        public SimpleRepository()
        {
            orders.Add(
                new Order
                {
                    Id = 1,
                    OrderProduct = products.ElementAt(0),
                    OrderDate = DateTime.Now,
                    OrderClient = clients[0]
                });

            orders.Add(
                new Order
                {
                    Id = 2,
                    OrderProduct = products.ElementAt(0),
                    OrderDate = DateTime.Now,
                    OrderClient = clients[0]
                });
        }


    }
}
