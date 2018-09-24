using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Windows.Forms;

namespace MainForm
{
    public partial class MainForm : Form
    {
        OpenFileDialog openFileDialog = new OpenFileDialog()
        {
            Filter = "Images|*.png;*.jpg"
        };
        /// <summary>
        /// Картинка в байтах
        /// </summary>
        byte[] Bitmapbytes;
        /// <summary>
        /// Количество байт в Bitmapbytes
        /// </summary>
        int BitmapbytesLen;
        /// <summary>
        /// Указание куда подключатся 
        /// </summary>
        IPAddress ipAddress;
        IPEndPoint remoteEP;
        /// <summary>
        /// Сокет
        /// </summary>
        Socket client;

        /// <summary>
        /// Конструктор
        /// </summary>
        public MainForm()
        {
            InitializeComponent();

            ipAddress = IPAddress.Parse("127.0.0.1"); ;
            remoteEP = new IPEndPoint(ipAddress, 10001);
        }
        /// <summary>
        /// Метод запускабющийся при нажатии на кнопку "Загрузить"
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void buttonLoadImg_Click(object sender, EventArgs e)
        {
            if (openFileDialog.ShowDialog() == DialogResult.OK)
            {
                Bitmap img = LoadBitmap(openFileDialog.FileName);

                pictureBox1.Image = img;
                this.buttonSend.Enabled = true;
            }
            else return;
        }

        /// <summary>
        /// Метод вызывающийся при нажатии на кнопку "Узнать"
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void buttonSend_Click(object sender, EventArgs e)
        {
            if (BitmapbytesLen > 2048)
            {
                MessageBox.Show("Пакет больше принимаемого", "Warning");
            }
            int ansver = GetInfoAboutImg();
        }

        /// <summary>
        /// Метод загрузки выбранного изображения и перевода его в байтовый формат
        /// </summary>
        /// <param name="fileName"></param>
        /// <returns></returns>
        private Bitmap LoadBitmap(string fileName)
        {
            Bitmap Img;
            using (FileStream fs = new FileStream(fileName, FileMode.Open, FileAccess.Read, FileShare.Read))
            {
                Img = new Bitmap(fs);
                if (Img.Height != 20 && Img.Width != 20)
                {
                    MessageBox.Show("Вы выбрали картинку с разрешением не равным 20х20. Результаты могут быть не точными.");
                }
            }
            // Изменение размера нужно для того чтобы передавать меньше, так как сервер обрабатывает изображения 20на20
            Img = resizeImage(Img, new Size(20, 20));
            // Этот немного костыльный код написанн из-за того что я не знаю как сделать иначе 
            using (FileStream saveStream = new FileStream("SendingImage.png", FileMode.Create, FileAccess.Write))
            {
                Img.Save(saveStream, ImageFormat.Png);
            }
            using (FileStream loadStream = new FileStream("SendingImage.png", FileMode.Open, FileAccess.Read))
            {
                Bitmapbytes = new byte[loadStream.Length];
                BitmapbytesLen = (int)loadStream.Length;
                int numBytesRead = 0;
                while (BitmapbytesLen > 0)
                {
                    // Read может вернуть любое значение между 0 и BitmapbytesLen
                    int n = loadStream.Read(Bitmapbytes, numBytesRead, BitmapbytesLen);
                    if (n == 0)
                        break;

                    numBytesRead += n;
                    BitmapbytesLen -= n;
                }
            }
            return Img;
        }

        /// <summary>
        /// Метод изменяющий размер изображения
        /// </summary>
        /// <param name="imgToResize"></param>
        /// <param name="size"></param>
        /// <returns></returns>
        public static Bitmap resizeImage(Bitmap imgToResize, Size size)
        {
            return new Bitmap(imgToResize, size);
        }

        /// <summary>
        /// Метод для отправки изображения и получения ответа от сервера
        /// </summary>
        /// <returns></returns>
        private int GetInfoAboutImg()
        {
            byte[] bytes = new byte[4]; 

            client = new Socket(ipAddress.AddressFamily,
                    SocketType.Stream, ProtocolType.Tcp);
            try
            {
                client.Connect(remoteEP);

                int BytesToSend = Bitmapbytes.Length;

                int bytesSent = client.Send(Bitmapbytes);
                // MessageBox.Show(string.Format("Отправлено {0}", bytesSent));

                int bytesRec = client.Receive(bytes);
                int ans = BitConverter.ToInt32(bytes, 0);
                this.Activate();
                string text = "";
                switch (ans)
                {
                    case 0:
                        text = "Не самолет";
                        break;
                    case 1:
                        text = "Самолет";
                        break;
                    default:
                        text = "Ошибка";
                        break;
                }
                textBox1.Text = text;
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
            finally
            {
                if (client.Connected)
                {
                    client.Shutdown(SocketShutdown.Both);
                    client.Close();

                }
            }
            return 0;
        }
    }
}
