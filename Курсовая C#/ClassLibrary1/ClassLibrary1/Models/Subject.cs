using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ClassLibrary1.Models
{
    public abstract class Subject
    {
        //Идентификатор
        public int Id { get; set; }
        //Имя
        public string Name { get; set; }
        //Описание
        public string? Description { get; set; }
    }
}
