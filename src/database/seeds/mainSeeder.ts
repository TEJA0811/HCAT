import { Seeder, runSeeder } from 'typeorm-extension';
import { DataSource } from 'typeorm';
import { UserSeeder } from './userSeeder';

export class MainSeeder implements Seeder {
  async run(dataSource: DataSource): Promise<void> {
    await runSeeder(dataSource, UserSeeder);
  }
}
