import { DataSource, DataSourceOptions } from 'typeorm';
import { config } from 'dotenv';
import { SeederOptions } from 'typeorm-extension';
import { MainSeeder } from '../database/seeds/mainSeeder';
import { User } from '../users/entities/user.entity';

config();

const options: DataSourceOptions & SeederOptions = {
  type: 'postgres',
  host: process.env.DATABASE_HOST,
  port: Number(process.env.DATABASE_PORT),
  username: process.env.DATABASE_USER,
  password: process.env.DATABASE_PASSWORD,
  database: process.env.DATABASE_NAME,
  entities: [__dirname + '/../**/entities/*.entity{.ts,.js}'],
  migrations: [__dirname + '/../database/migrations/*{.ts,.js}'],
  seeds: [MainSeeder],
  synchronize: false,
  logging: true,
};

const AppDataSource = new DataSource(options);

AppDataSource.initialize();

export { AppDataSource };
